from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# --- CATEGORY SCHEMAS ---

class CategoryBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryResponse(CategoryBase):
    id_category: int

    class Config:
        from_attributes = True


# --- PRODUCT SCHEMAS ---

class ProductBase(BaseModel):
    reference: str = Field(..., max_length=50, description="SKU / Code Référence unique")
    label: str = Field(..., max_length=150, description="Désignation du produit")
    description: Optional[str] = None
    category_id: Optional[int] = None
    price_purchase: float = Field(default=0.0, ge=0.0)
    price_sell: float = Field(default=0.0, ge=0.0)
    status: str = Field(default="ACTIF", description="ACTIF, INACTIF, REAPPRO")
    stock_quantity: int = Field(default=0, ge=0)
    stock_reserved: int = Field(default=0, ge=0)
    stock_min: int = Field(default=5, ge=0)
    stock_max: int = Field(default=100, ge=0)


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    reference: Optional[str] = None
    label: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    price_purchase: Optional[float] = None
    price_sell: Optional[float] = None
    status: Optional[str] = None
    stock_quantity: Optional[int] = None
    stock_reserved: Optional[int] = None
    stock_min: Optional[int] = None
    stock_max: Optional[int] = None


class ProductResponse(ProductBase):
    id_product: int
    created_at: datetime
    updated_at: datetime
    category: Optional[CategoryResponse] = None
    stock_available: int = 0

    class Config:
        from_attributes = True


# --- STOCK MOVEMENT SCHEMAS ---

class StockMovementCreate(BaseModel):
    movement_type: str = Field(..., description="ENTREE, SORTIE, AJUSTEMENT, TRANSFERT")
    quantity: int = Field(..., description="Quantité déplacée (positive ou négative)")
    reference_doc: Optional[str] = None
    comment: Optional[str] = None


class StockMovementResponse(BaseModel):
    id_movement: int
    product_id: int
    movement_type: str
    quantity: int
    reference_doc: Optional[str] = None
    comment: Optional[str] = None
    created_at: datetime
    created_by_user_id: Optional[int] = None

    class Config:
        from_attributes = True
