from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import require_permission, require_all_permissions, get_db
from app.schemas.users.user import UserResponse
from app.schemas.purchases.purchase import (
    SupplierCreate,
    SupplierResponse,
    PurchaseRequisitionCreate,
    PurchaseRequisitionResponse,
    RequisitionValidationRequest,
    PurchaseOrderCreate,
    PurchaseOrderResponse,
    GoodsReceiptCreate,
    GoodsReceiptResponse,
    SupplierInvoiceCreate,
    SupplierInvoiceResponse,
    SupplierAnalysisResponse,
    AIRecommendationRequest
)
from app.services.purchases import purchase_service

router = APIRouter(prefix="/purchases", tags=["Purchases & Suppliers"])


@router.get("/overview")
async def get_purchases_overview(
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(require_permission("PURCHASE_READ"))
):
    """Récupère les KPIs globaux des Achats & Fournisseurs."""
    return await purchase_service.get_purchases_overview(db)


# --- FOURNISSEURS ---

@router.get("/suppliers", response_model=List[SupplierResponse])
async def list_suppliers(
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(require_permission("SUPPLIER_READ", "PURCHASE_READ"))
):
    """Liste tous les fournisseurs (synchro Dolibarr + local)."""
    return await purchase_service.get_suppliers(db)


@router.post("/suppliers", response_model=SupplierResponse, status_code=status.HTTP_201_CREATED)
async def create_supplier(
    supplier_data: SupplierCreate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(require_permission("SUPPLIER_CREATE", "PURCHASE_CREATE"))
):
    """Créer un nouveau fournisseur."""
    return await purchase_service.create_supplier(
        db,
        supplier_data.dict(),
        actor_user_id=current_user.id_user
    )


@router.put("/suppliers/{supplier_id}", response_model=SupplierResponse, summary="Modifier un fournisseur")
async def update_supplier(
    supplier_id: int,
    supplier_data: SupplierCreate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(require_permission("SUPPLIER_UPDATE", "PURCHASE_UPDATE"))
):
    try:
        return await purchase_service.update_supplier(
            db, supplier_id, supplier_data.dict(exclude_unset=True), actor_user_id=current_user.id_user
        )
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/suppliers/{supplier_id}", status_code=status.HTTP_200_OK, summary="Supprimer ou désactiver un fournisseur")
async def delete_supplier(
    supplier_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(require_permission("SUPPLIER_DELETE", "PURCHASE_UPDATE"))
):
    try:
        await purchase_service.delete_supplier(db, supplier_id, actor_user_id=current_user.id_user)
        return {"message": "Fournisseur supprimé ou désactivé avec succès"}
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# --- DEMANDES D'ACHAT ---

@router.get("/requisitions", response_model=List[PurchaseRequisitionResponse])
async def list_purchase_requisitions(
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(require_permission("PURCHASE_READ"))
):
    """Liste des demandes d'achat."""
    return purchase_service.get_purchase_requisitions(db)


@router.post("/requisitions", response_model=PurchaseRequisitionResponse, status_code=status.HTTP_201_CREATED)
async def create_purchase_requisition(
    req_data: PurchaseRequisitionCreate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(require_permission("PURCHASE_CREATE"))
):
    """Créer une nouvelle demande d'achat (Étape 1 du workflow)."""
    return await purchase_service.create_purchase_requisition(
        db,
        req_data.dict(),
        user_id=current_user.id_user
    )


@router.put("/requisitions/{requisition_id}/validate", response_model=PurchaseRequisitionResponse)
async def validate_purchase_requisition(
    requisition_id: int,
    validation: RequisitionValidationRequest,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(require_permission("PURCHASE_VALIDATE"))
):
    """Validation ou Rejet d'une demande d'achat (Étape 2 du workflow - Opération sensible)."""
    try:
        return purchase_service.validate_purchase_requisition(
            db,
            requisition_id=requisition_id,
            action=validation.action,
            comment=validation.comment,
            actor_user_id=current_user.id_user
        )
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# --- COMMANDES D'ACHAT ---

@router.get("/orders", response_model=List[PurchaseOrderResponse])
async def list_purchase_orders(
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(require_permission("PURCHASE_READ"))
):
    """Liste des commandes d'achat."""
    return purchase_service.get_purchase_orders(db)


@router.post("/orders", response_model=PurchaseOrderResponse, status_code=status.HTTP_201_CREATED)
async def create_purchase_order(
    order_data: PurchaseOrderCreate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(require_permission("PURCHASE_CREATE"))
):
    """Créer une commande d'achat (Étape 3 du workflow)."""
    return await purchase_service.create_purchase_order(
        db,
        order_data.dict(),
        actor_user_id=current_user.id_user
    )


# --- RÉCEPTION & CONTRÔLE DE QUALITÉ ---

@router.get("/receipts", response_model=List[GoodsReceiptResponse])
async def list_goods_receipts(
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(require_permission("PURCHASE_READ"))
):
    """Liste des réceptions et contrôles de qualité."""
    return purchase_service.get_goods_receipts(db)


@router.post("/orders/receipt", response_model=GoodsReceiptResponse, status_code=status.HTTP_201_CREATED)
async def record_goods_receipt(
    receipt_data: GoodsReceiptCreate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(require_all_permissions("PURCHASE_UPDATE", "STOCK_UPDATE"))
):
    """
    Enregistrer une réception de marchandise & contrôle qualité (Étape 4 & 5 du workflow).
    Met à jour immédiatement le stock physique et réel (Exige à la fois PURCHASE_UPDATE et STOCK_UPDATE).
    """
    try:
        return await purchase_service.record_goods_receipt(
            db,
            receipt_data.dict(),
            actor_user_id=current_user.id_user
        )
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# --- FACTURES FOURNISSEURS ---

@router.get("/invoices", response_model=List[SupplierInvoiceResponse])
async def list_supplier_invoices(
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(require_permission("PURCHASE_READ"))
):
    """Liste des factures fournisseurs."""
    return purchase_service.get_supplier_invoices(db)


@router.post("/invoices", response_model=SupplierInvoiceResponse, status_code=status.HTTP_201_CREATED)
async def create_supplier_invoice(
    inv_data: SupplierInvoiceCreate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(require_permission("PURCHASE_CREATE", "PURCHASE_UPDATE"))
):
    """Créer et valider une facture fournisseur (Étape 6 du workflow)."""
    try:
        return purchase_service.create_supplier_invoice(
            db,
            inv_data.dict(),
            actor_user_id=current_user.id_user
        )
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# --- MODULE 6 : ANALYSE DES FOURNISSEURS & SCORE IA ---

@router.get("/analysis", response_model=List[SupplierAnalysisResponse])
async def get_supplier_analysis(
    price_weight: float = 0.30,
    delay_weight: float = 0.25,
    quality_weight: float = 0.25,
    reliability_weight: float = 0.20,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(require_permission("PURCHASE_READ"))
):
    """
    MODULE 6 — Analyse de performance et Score Fournisseurs (Prix 30%, Délai 25%, Qualité 25%, Fiabilité 20%).
    """
    weights = {
        "price_weight": price_weight,
        "delay_weight": delay_weight,
        "quality_weight": quality_weight,
        "reliability_weight": reliability_weight
    }
    return await purchase_service.get_supplier_performance_analysis(db, weights=weights)


@router.post("/analysis/recommend")
async def get_ai_supplier_recommendation(
    req: AIRecommendationRequest,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(require_permission("PURCHASE_READ"))
):
    """
    MODULE 6 — Recommandation IA du meilleur fournisseur selon la stratégie choisie.
    """
    return await purchase_service.get_ai_supplier_recommendation(
        db,
        priority=req.priority_criterion,
        product_id=req.product_id
    )
