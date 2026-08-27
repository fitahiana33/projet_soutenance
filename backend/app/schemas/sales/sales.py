from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class CustomerCreate(BaseModel):
    name: str = Field(..., description="Nom de l'entreprise client")
    code_client: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    siret_nif: Optional[str] = None
    payment_terms: str = Field("30_DAYS", description="Conditions de règlement (CASH, 30_DAYS, 60_DAYS)")


class CustomerResponse(BaseModel):
    id_customer: int
    name: str
    code_client: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    payment_terms: str
    total_revenue_generated: float = 0.0
    status: str = "ACTIF"
    created_at: str


class SaleQuoteCreate(BaseModel):
    customer_id: int
    items: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Liste des articles [{product_id, quantity, unit_price, discount_percent}]")
    notes: Optional[str] = None
    validity_days: int = 30


class SaleOrderCreate(BaseModel):
    customer_id: int
    quote_id: Optional[int] = None
    items: List[Dict[str, Any]] = Field(..., description="Liste des articles [{product_id, quantity, unit_price}]")
    shipping_address: Optional[str] = None
    comment: Optional[str] = None


class SaleOrderResponse(BaseModel):
    id_order: int
    order_ref: str
    customer_id: int
    customer_name: str
    total_amount_ht: float
    total_amount_ttc: float
    total_tva: float = 0.0
    vat_rate: float = 20.0
    discount_percent: float = 0.0
    items: List[Dict[str, Any]] = Field(default_factory=list)
    items_count: int
    status: str  # BROUILLON, VALIDEE, EN_LIVRAISON, LIVREE, FACTUREE, ANNULEE
    stock_reserved: bool
    created_at: str


class SaleDeliveryCreate(BaseModel):
    order_id: int
    reference: Optional[str] = Field(None, description="Référence idempotente de livraison")
    status: str = Field("PREPAREE", description="PREPAREE ou LIVREE")
    total_quantity: Optional[int] = Field(None, ge=0)
    delivery_date: Optional[str] = None
    tracking_number: Optional[str] = None
    carrier: Optional[str] = None
    customer_signature: Optional[bool] = None
    notes: Optional[str] = None


class SaleInvoiceCreate(BaseModel):
    order_id: int
    payment_mode: str = Field("VIREMENT", description="VIREMENT, CHEQUE, ESPÈCES, CB")
    notes: Optional[str] = None
    invoice_date: Optional[str] = None


class DeliveryCreate(BaseModel):
    order_id: int
    reference: Optional[str] = None
    status: str = Field("PREPAREE", description="PREPAREE ou LIVREE")
    delivery_date: Optional[str] = None
    total_quantity: Optional[int] = Field(None, ge=0)
    tracking_number: Optional[str] = None
    carrier: Optional[str] = None
    customer_signature: Optional[bool] = None
    notes: Optional[str] = None


class SalePaymentUpdate(BaseModel):
    amount_paid: float = Field(..., ge=0.0)
    payment_mode: Optional[str] = None
    payment_ref: Optional[str] = None


class SaleInvoiceResponse(BaseModel):
    id_invoice: int
    invoice_ref: str
    order_id: int
    order_ref: Optional[str] = None
    customer_id: Optional[int] = None
    customer_name: str
    total_amount_ttc: float
    total_amount_ht: float = 0.0
    total_tva: float = 0.0
    vat_rate: float = 20.0
    discount_percent: float = 0.0
    items: List[Dict[str, Any]] = Field(default_factory=list)
    amount_paid: float
    balance_due: float
    status: str  # NON_PAYEE, PARTIELLEMENT_PAYEE, PAYEE
    payment_mode: Optional[str] = None
    invoice_date: Optional[str] = None
    created_at: str
