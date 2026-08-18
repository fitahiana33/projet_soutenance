from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.users.user import User
from app.api.deps import require_permission
from app.schemas.sales.sales import (
    CustomerCreate, CustomerResponse,
    SaleQuoteCreate, SaleOrderCreate, SaleOrderResponse,
    SaleInvoiceCreate, SaleInvoiceResponse
)
from app.services.sales import sales_service
from app.services.audit.audit_service import log_action

router = APIRouter(prefix="/sales", tags=["Gestion des Ventes & Clients"])


@router.get("/overview", summary="Obtenir les KPIs généraux des ventes")
async def read_sales_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("STOCK_READ"))
):
    return sales_service.get_sales_overview(db)


@router.get("/customers", response_model=List[CustomerResponse], summary="Référentiel des clients")
async def read_customers(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("STOCK_READ"))
):
    return await sales_service.get_all_customers(db)


@router.post("/customers", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED, summary="Créer une fiche client")
async def add_customer(
    data: CustomerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("STOCK_WRITE"))
):
    res = sales_service.create_customer(db, data.model_dump(), actor_user=current_user)
    return res


@router.get("/quotes", summary="Liste des devis clients")
async def read_quotes(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("STOCK_READ"))
):
    return sales_service.get_sales_quotes(db)


@router.post("/quotes", status_code=status.HTTP_201_CREATED, summary="Créer un devis de vente")
async def add_quote(
    data: SaleQuoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("STOCK_WRITE"))
):
    res = await sales_service.create_sales_quote(db, data.model_dump(), actor_user=current_user)
    return res


@router.get("/orders", response_model=List[SaleOrderResponse], summary="Historique des commandes clients")
async def read_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("STOCK_READ"))
):
    return sales_service.get_sales_orders(db)


@router.post("/orders", response_model=SaleOrderResponse, status_code=status.HTTP_201_CREATED, summary="Créer une commande client")
async def add_order(
    data: SaleOrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("STOCK_WRITE"))
):
    res = await sales_service.create_sales_order(db, data.model_dump(), actor_user=current_user)
    return res


@router.put("/orders/{order_id}/status", summary="Mettre à jour le statut d'une commande (Valider / Livrer / Annuler)")
async def change_order_status(
    order_id: int,
    status_val: str = Query(..., alias="status", description="Nouveau statut (VALIDEE, LIVREE, ANNULEE)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("STOCK_WRITE"))
):
    try:
        res = sales_service.update_sales_order_status(db, order_id, status_val, actor_user=current_user)
        return res
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/invoices", response_model=List[SaleInvoiceResponse], summary="Factures et règlements clients")
async def read_invoices(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("STOCK_READ"))
):
    return sales_service.get_sales_invoices(db)


@router.post("/invoices", response_model=SaleInvoiceResponse, status_code=status.HTTP_201_CREATED, summary="Générer une facture client")
async def add_invoice(
    data: SaleInvoiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("STOCK_WRITE"))
):
    res = sales_service.create_sales_invoice(db, data.model_dump(), actor_user=current_user)
    return res
