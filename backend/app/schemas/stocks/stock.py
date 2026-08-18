from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class StockMovementCreate(BaseModel):
    product_id: int
    movement_type: str = Field(..., description="ENTREE, SORTIE, TRANSFERT, AJUSTEMENT")
    quantity: int = Field(..., description="Quantité du mouvement")
    reference_doc: Optional[str] = None
    comment: Optional[str] = None
    warehouse_id: Optional[int] = None
    lot_number: Optional[str] = None


class StockMovementResponse(BaseModel):
    id_movement: int
    product_id: int
    product_label: Optional[str] = None
    product_ref: Optional[str] = None
    movement_type: str
    quantity: int
    unit_price: Optional[float] = None
    reference_doc: Optional[str] = None
    comment: Optional[str] = None
    lot_number: Optional[str] = None
    created_at: str
    created_by_user_id: Optional[int] = 1


class StockOverviewResponse(BaseModel):
    total_products: int
    total_physical_stock: int
    total_available_stock: int
    total_reserved_stock: int
    low_stock_count: int
    out_of_stock_count: int
    total_stock_value: float


class ProductValuationDetail(BaseModel):
    product_id: int
    reference: str
    label: str
    stock_quantity: int
    unit_cost_price: float
    cump_unit_price: float
    fifo_unit_price: float
    total_value_cost_price: float
    total_value_cump: float
    total_value_fifo: float
    variance_cump_fifo: float
    entry_lots_count: Optional[int] = 0


class StockValuationResponse(BaseModel):
    valuation_method: str
    total_inventory_value: float
    total_value_cump: Optional[float] = None
    total_value_fifo: Optional[float] = None
    variance_total: Optional[float] = None
    products: List[ProductValuationDetail]


class StockRotationDetail(BaseModel):
    product_id: int
    reference: str
    label: str
    current_stock: Optional[int] = 0
    average_stock: float
    total_outflow: Optional[int] = 0
    annualized_outflow: Optional[int] = 0
    turnover_rate: float
    average_retention_days: float
    rotation_speed: str  # RAPIDE, MOYENNE, LENTE, DORMANT


class ProductLotCreate(BaseModel):
    product_id: int
    batch_number: str
    serial_number: Optional[str] = None
    expiration_date: Optional[str] = None
    quantity: int = 0
    supplier_ref: Optional[str] = None


class ProductLotResponse(BaseModel):
    id_lot: int
    product_id: int
    product_ref: Optional[str] = None
    product_label: Optional[str] = None
    batch_number: str
    serial_number: Optional[str] = None
    expiration_date: Optional[str] = None
    quantity: int
    status: str  # VALIDE, EXPIRE, ALERTE_PROCHE
    is_blocked: bool
    created_at: str
