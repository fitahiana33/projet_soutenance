import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query

from app.api.deps import require_permission, get_current_user, get_db
from sqlalchemy.orm import Session
from app.models.users.user import User
from app.schemas.products.product import (
    CategoryCreate,
    CategoryResponse,
    ProductCreate,
    ProductResponse,
    ProductUpdate,
    StockMovementCreate,
    StockMovementResponse
)
from app.services.products.product_service import (
    create_category,
    update_category,
    delete_category,
    create_product,
    delete_product,
    get_all_categories,
    get_all_products,
    get_product_by_id,
    get_product_movements,
    record_stock_movement,
    update_product
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/products",
    tags=["Products & Stock Repository (Dolibarr ERP)"]
)


# ============================================================
# CATEGORIES ENDPOINTS
# ============================================================

@router.get(
    "/categories",
    response_model=List[CategoryResponse],
    summary="Lister toutes les catégories de produits depuis Dolibarr"
)
async def list_categories(
    current_user: User = Depends(require_permission("STOCK_READ"))
):
    try:
        return await get_all_categories()
    except Exception as e:
        logger.error(f"Error listing categories: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des catégories Dolibarr"
        ) from e


@router.post(
    "/categories",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Créer une nouvelle catégorie de produit"
)
async def create_new_category(
    category_in: CategoryCreate,
    current_user: User = Depends(require_permission("STOCK_UPDATE"))
):
    try:
        return await create_category(category_in.name, category_in.description)
    except Exception as e:
        logger.error(f"Error creating category: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Impossible de créer la catégorie"
        ) from e


@router.put(
    "/categories/{category_id}",
    response_model=CategoryResponse,
    summary="Modifier une catégorie de produit"
)
async def update_existing_category(
    category_id: int,
    category_in: CategoryCreate,
    current_user: User = Depends(require_permission("STOCK_UPDATE"))
):
    try:
        return await update_category(category_id, category_in.name, category_in.description)
    except Exception as e:
        logger.error(f"Error updating category {category_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la modification de la catégorie"
        ) from e


@router.delete(
    "/categories/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Supprimer une catégorie de produit"
)
async def delete_existing_category(
    category_id: int,
    current_user: User = Depends(require_permission("STOCK_UPDATE"))
):
    try:
        await delete_category(category_id)
        return None
    except Exception as e:
        logger.error(f"Error deleting category {category_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la suppression de la catégorie"
        ) from e


# ============================================================
# PRODUCTS CRUD ENDPOINTS (DOLIBARR REST API)
# ============================================================

@router.get(
    "/",
    response_model=List[ProductResponse],
    summary="Lister, rechercher et filtrer le référentiel produits depuis Dolibarr ERP"
)
async def list_products(
    q: Optional[str] = Query(None, description="Recherche par désignation, référence SKU ou description"),
    category_id: Optional[int] = Query(None, description="Filtrer par catégorie"),
    status: Optional[str] = Query(None, description="Filtrer par état (ACTIF, INACTIF, REAPPRO)"),
    stock_status: Optional[str] = Query(None, description="Filtrer par état de stock (ok, low, out)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("STOCK_READ"))
):
    try:
        return await get_all_products(
            q=q,
            category_id=category_id,
            status=status,
            stock_status=stock_status,
            db=db
        )
    except Exception as e:
        logger.error(f"Error listing Dolibarr products: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des produits Dolibarr"
        ) from e


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Récupérer un produit Dolibarr par ID"
)
async def get_product(
    product_id: int,
    current_user: User = Depends(require_permission("STOCK_READ"))
):
    try:
        product = await get_product_by_id(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Produit introuvable dans Dolibarr ERP"
            )
        return product
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching product {product_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur serveur"
        ) from e


@router.post(
    "/",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Créer un nouveau produit Dolibarr"
)
async def create_new_product(
    product_in: ProductCreate,
    current_user: User = Depends(require_permission("STOCK_UPDATE"))
):
    try:
        return await create_product(product_in.model_dump())
    except Exception as e:
        logger.error(f"Error creating Dolibarr product: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la création du produit dans Dolibarr"
        ) from e


@router.put(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Modifier un produit Dolibarr existant"
)
async def update_existing_product(
    product_id: int,
    product_in: ProductUpdate,
    current_user: User = Depends(require_permission("STOCK_UPDATE"))
):
    try:
        updated = await update_product(product_id, product_in.model_dump(exclude_unset=True))
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Produit introuvable"
            )
        return updated
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating product {product_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la modification du produit Dolibarr"
        ) from e


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Supprimer un produit Dolibarr"
)
async def delete_existing_product(
    product_id: int,
    current_user: User = Depends(require_permission("STOCK_UPDATE"))
):
    try:
        success = await delete_product(product_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Produit introuvable"
            )
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting product {product_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la suppression du produit Dolibarr"
        ) from e


# ============================================================
# STOCK MOVEMENTS ENDPOINTS (DOLIBARR REST API)
# ============================================================

@router.get(
    "/{product_id}/movements",
    response_model=List[StockMovementResponse],
    summary="Consulter l'historique des mouvements de stock Dolibarr d'un produit"
)
async def list_product_movements(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("STOCK_READ"))
):
    try:
        return await get_product_movements(product_id, db=db)
    except Exception as e:
        logger.error(f"Error fetching stock movements for product {product_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération de l'historique des mouvements Dolibarr"
        ) from e


@router.post(
    "/{product_id}/movements",
    response_model=StockMovementResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Enregistrer un mouvement de stock Dolibarr pour un produit"
)
async def add_stock_movement(
    product_id: int,
    movement_in: StockMovementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("STOCK_UPDATE"))
):
    try:
        return await record_stock_movement(
            product_id=product_id,
            movement_type=movement_in.movement_type,
            quantity=movement_in.quantity,
            reference_doc=movement_in.reference_doc,
            comment=movement_in.comment,
            user_id=current_user.id_user,
            db=db
        )
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(val_err)
        )
    except Exception as e:
        logger.error(f"Error recording movement for product {product_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de l'enregistrement du mouvement de stock Dolibarr"
        ) from e
