from datetime import datetime, timezone, date
from typing import Optional
from sqlalchemy import (
    Integer, String, Float, DateTime, Date, ForeignKey, Boolean, Text
)
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.core.database import Base
from app.models.products.product import Product


class ProductLot(Base):
    __tablename__ = "product_lots"

    id_lot: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    lot_number: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    serial_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("products.id_product"), nullable=False
    )
    product_label: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    product_ref: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    initial_quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    unit_price: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    supplier_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    supplier_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    purchase_order_ref: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    manufacture_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    expiry_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True, index=True)
    reception_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    warehouse: Mapped[str] = mapped_column(String(100), nullable=False, default="Principal")
    location: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    status: Mapped[str] = mapped_column(String(30), nullable=False, default="DISPONIBLE", index=True)
    is_blocked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    block_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_by_user_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    product: Mapped[Product] = relationship("Product")

    @property
    def is_expired(self) -> bool:
        if not self.expiry_date:
            return False
        return self.expiry_date < datetime.now(timezone.utc).date()

    @property
    def days_until_expiry(self) -> Optional[int]:
        if not self.expiry_date:
            return None
        delta = self.expiry_date - datetime.now(timezone.utc).date()
        return delta.days
