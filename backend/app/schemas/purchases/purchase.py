from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class SupplierBase(BaseModel):
    name: str = Field(..., description="Nom du fournisseur")
    code: Optional[str] = Field(None, description="Code fournisseur (ex: FOURN-001)")
    email: Optional[str] = Field(None, description="Email de contact")
    phone: Optional[str] = Field(None, description="Numéro de téléphone")
    address: Optional[str] = Field(None, description="Adresse physique")
    status: str = Field("ACTIF", description="Statut (ACTIF, INACTIF)")


class SupplierCreate(SupplierBase):
    pass


class SupplierResponse(SupplierBase):
    id_supplier: int
    dolibarr_id: Optional[int] = None
    created_at: str


class PurchaseRequisitionCreate(BaseModel):
    product_id: int
    supplier_id: Optional[int] = None
    quantity: int = Field(..., gt=0)
    estimated_unit_price: float = Field(..., ge=0.0)
    reason: Optional[str] = None


class PurchaseRequisitionResponse(BaseModel):
    id_requisition: int
    reference: str
    product_id: int
    product_label: str
    product_ref: str
    supplier_id: Optional[int] = None
    supplier_name: Optional[str] = None
    quantity: int
    estimated_unit_price: float
    total_estimated: float
    status: str  # DEMANDE, VALIDEE, REJETEE, COMMANDEE
    reason: Optional[str] = None
    created_by_user_id: Optional[int] = None
    created_at: str
    validated_at: Optional[str] = None


class RequisitionValidationRequest(BaseModel):
    action: str = Field(..., description="VALIDER ou REJETER")
    comment: Optional[str] = None


class PurchaseOrderCreate(BaseModel):
    requisition_id: Optional[int] = None
    supplier_id: int
    product_id: int
    quantity: int = Field(..., gt=0)
    unit_price: float = Field(..., ge=0.0)
    expected_delivery_date: Optional[str] = None
    notes: Optional[str] = None


class PurchaseOrderResponse(BaseModel):
    id_order: int
    reference: str
    requisition_id: Optional[int] = None
    supplier_id: int
    supplier_name: str
    product_id: int
    product_label: str
    product_ref: str
    quantity: int
    unit_price: float
    total_amount: float
    status: str  # EN_ATTENTE, VALIDEE, COMMANDEE, PARTIELLEMENT_RECUE, RECUE, ANNULEE
    order_date: str
    expected_delivery_date: Optional[str] = None
    actual_delivery_date: Optional[str] = None


class GoodsReceiptCreate(BaseModel):
    order_id: int
    quantity_received: int = Field(..., gt=0)
    quality_control_status: str = Field("CONFORME", description="CONFORME, NON_CONFORME, AVEC_RESERVES")
    quality_notes: Optional[str] = None


class GoodsReceiptResponse(BaseModel):
    id_receipt: int
    reference: str
    order_id: int
    order_ref: str
    product_label: str
    quantity_received: int
    quality_control_status: str
    quality_notes: Optional[str] = None
    received_at: str


class SupplierInvoiceCreate(BaseModel):
    order_id: int
    invoice_number: str
    amount_ht: float = Field(..., ge=0.0)
    vat_rate: float = Field(20.0, ge=0.0)
    invoice_date: Optional[str] = None


class SupplierInvoiceResponse(BaseModel):
    id_invoice: int
    invoice_number: str
    order_id: int
    order_ref: str
    supplier_name: str
    amount_ht: float
    vat_rate: float
    amount_ttc: float
    status: str  # BROUILLON, VALIDEE, PAYEE
    invoice_date: str


class SupplierScoreWeights(BaseModel):
    price_weight: float = Field(0.30, ge=0.0, le=1.0)
    delay_weight: float = Field(0.25, ge=0.0, le=1.0)
    quality_weight: float = Field(0.25, ge=0.0, le=1.0)
    reliability_weight: float = Field(0.20, ge=0.0, le=1.0)


class SupplierAnalysisResponse(BaseModel):
    supplier_id: int
    supplier_name: str
    total_orders: int
    avg_price: float
    avg_delivery_days: float
    delay_rate_percent: float
    conformity_rate_percent: float
    quality_score: float  # / 100
    order_frequency_per_year: float
    price_trend: str  # HAISSE, STABLE, BAISSE
    score_price: float
    score_delay: float
    score_quality: float
    score_reliability: float
    overall_score_percent: float
    recommendation_badge: str  # RECOMMANDÉ, ACCEPTABLE, À RISQUE


class AIRecommendationRequest(BaseModel):
    priority_criterion: str = Field("BALANCED", description="BALANCED, PRIX, DELAI, QUALITE, FIABILITE")
    product_id: Optional[int] = None
