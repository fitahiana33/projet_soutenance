from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.users.user import User
from app.api.deps import require_permission
from app.schemas.stocks.stock import (
    StockMovementCreate,
    StockMovementResponse,
    StockOverviewResponse,
    StockValuationResponse,
    StockRotationDetail,
    ProductLotCreate,
    ProductLotResponse
)
from app.services.stocks.stock_service import (
    get_stock_overview,
    get_stock_movements,
    get_stock_valuation,
    get_stock_rotation,
    get_product_lots,
    create_product_lot,
    save_stock_snapshot,
    reconcile_pending_stock_movements,
)
from app.services.products.product_service import record_stock_movement

router = APIRouter(prefix="/stocks", tags=["Gestion des Stocks & Inventaires"])


@router.get(
    "/overview",
    response_model=StockOverviewResponse,
    summary="Obtenir la synthèse globale des stocks (métriques, alertes et valorisation)"
)
async def read_stock_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("STOCK_READ"))
):
    return await get_stock_overview(db=db)


@router.get(
    "/movements",
    response_model=List[StockMovementResponse],
    summary="Historique complet des mouvements de stock (Entrées, Sorties, Ajustements)"
)
async def read_stock_movements(
    product_id: Optional[int] = Query(None, description="Filtrer par ID produit"),
    movement_type: Optional[str] = Query(None, description="ENTREE, SORTIE, TRANSFERT, AJUSTEMENT"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("STOCK_READ"))
):
    return await get_stock_movements(product_id=product_id, movement_type=movement_type, db=db)


@router.post(
    "/movements",
    response_model=StockMovementResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Enregistrer un nouveau mouvement de stock"
)
async def create_stock_movement(
    data: StockMovementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("STOCK_UPDATE"))
):
    try:
        res = await record_stock_movement(
            product_id=data.product_id,
            movement_type=data.movement_type,
            quantity=data.quantity,
            reference_doc=data.reference_doc,
            comment=data.comment,
            user_id=current_user.id_user,
            db=db
        )
        return res
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erreur lors de l'enregistrement du mouvement: {str(e)}"
        )


@router.get(
    "/valuation",
    response_model=StockValuationResponse,
    summary="Valorisation financière du stock (CUMP, FIFO et Comparaison)"
)
async def read_stock_valuation(
    method: str = Query("ALL", description="Méthode de valorisation: CUMP, FIFO, ALL"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("STOCK_READ"))
):
    return await get_stock_valuation(method=method, db=db)


@router.get(
    "/rotation",
    response_model=List[StockRotationDetail],
    summary="Analyse du Taux de Rotation des stocks et Vitesse de rotation"
)
async def read_stock_rotation(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("STOCK_READ"))
):
    return await get_stock_rotation(db=db)


@router.get(
    "/lots",
    response_model=List[ProductLotResponse],
    summary="Gestion des Lots, Numéros de série et Traçabilité FEFO"
)
async def read_product_lots(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("STOCK_READ"))
):
    return await get_product_lots(db)


@router.post(
    "/lots",
    response_model=ProductLotResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Créer et enregistrer un lot / numéro de série avec date d'expiration"
)
async def create_lot(
    data: ProductLotCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("STOCK_UPDATE"))
):
    res = await create_product_lot(db, data.model_dump(), user_id=current_user.id_user)
    return {
        "id_lot": res["id_lot"],
        "product_id": res["product_id"],
        "product_ref": f"PRD-{res['product_id']}",
        "product_label": "Produit",
        "batch_number": res["batch_number"],
        "serial_number": res.get("serial_number"),
        "expiration_date": res.get("expiration_date"),
        "quantity": res.get("quantity", 0),
        "status": "VALIDE",
        "is_blocked": False,
        "created_at": res["created_at"]
    }

@router.post(
    "/snapshot",
    summary="Persister un instantané quotidien du stock pour le module IA (action explicite)",
    status_code=status.HTTP_201_CREATED,
)
async def create_stock_snapshot(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("STOCK_READ"))
):
    """Déclenche la sauvegarde d'un snapshot IA pour la date du jour.
    Idempotent : appeler deux fois le même jour met simplement à jour le snapshot existant.
    """
    try:
        return await save_stock_snapshot(db=db)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la création du snapshot: {str(e)}"
        )


@router.post(
    "/movements/reconcile",
    summary="Réconcilier les mouvements stock en attente avec Dolibarr",
)
async def reconcile_stock_movements(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("STOCK_UPDATE")),
):
    try:
        return await reconcile_pending_stock_movements(db=db)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Erreur lors de la réconciliation Dolibarr: {str(e)}",
        )


@router.put(
    "/lots/{id_lot}/block",
    summary="Bloquer ou débloquer un lot (quarantaine, retrait marche)"
)
def toggle_lot_block(
    id_lot: int,
    blocked: bool,
    reason: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("STOCK_UPDATE"))
):
    """Bloque (blocked=true) ou débloque (blocked=false) un lot.
    Un lot bloqué ne peut pas être utilisé dans les sorties FEFO.
    """
    from app.models.stocks.lots import ProductLot
    lot = db.query(ProductLot).filter(ProductLot.id_lot == id_lot).first()
    if not lot:
        raise HTTPException(status_code=404, detail=f"Lot #{id_lot} introuvable.")
    lot.is_blocked = blocked
    lot.block_reason = reason if blocked else None
    db.commit()
    db.refresh(lot)
    return {
        "id_lot": lot.id_lot,
        "lot_number": lot.lot_number,
        "product_id": lot.product_id,
        "is_blocked": lot.is_blocked,
        "block_reason": lot.block_reason,
    }
