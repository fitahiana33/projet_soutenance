from datetime import datetime, timezone, date
from typing import Optional, List
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, Date,
    ForeignKey, Text
)
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.core.database import Base


class Supplier(Base):
    __tablename__ = "suppliers"

    id_supplier: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    dolibarr_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    email: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    country: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    tax_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="ACTIF")
    payment_terms_days: Mapped[int] = mapped_column(Integer, nullable=False, default=30)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    orders: Mapped[List["PurchaseOrder"]] = relationship("PurchaseOrder", back_populates="supplier")


class PurchaseRequisition(Base):
    __tablename__ = "purchase_requisitions"

    id_requisition: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    reference: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    product_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    product_label: Mapped[str] = mapped_column(String(200), nullable=False)
    product_ref: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    supplier_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("suppliers.id_supplier"), nullable=True
    )
    supplier_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    estimated_unit_price: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    total_estimated: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="DEMANDE", index=True)
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_by_user_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    validated_by_user_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    validated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    supplier: Mapped[Optional[Supplier]] = relationship("Supplier")


class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    id_order: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    reference: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    requisition_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    supplier_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("suppliers.id_supplier"), nullable=False
    )
    supplier_name: Mapped[str] = mapped_column(String(200), nullable=False)
    product_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    product_label: Mapped[str] = mapped_column(String(200), nullable=False)
    product_ref: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    total_amount: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    vat_rate: Mapped[float] = mapped_column(Float, nullable=False, default=20.0)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="COMMANDEE", index=True)
    order_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    expected_delivery_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    actual_delivery_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
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

    supplier: Mapped[Supplier] = relationship("Supplier", back_populates="orders")
    receipts: Mapped[List["GoodsReceipt"]] = relationship(
        "GoodsReceipt", back_populates="purchase_order"
    )
    invoices: Mapped[List["SupplierInvoice"]] = relationship(
        "SupplierInvoice", back_populates="purchase_order"
    )
    lines: Mapped[List["PurchaseOrderLine"]] = relationship(
        "PurchaseOrderLine", back_populates="order", cascade="all, delete-orphan"
    )


class PurchaseOrderLine(Base):
    __tablename__ = "purchase_order_lines"

    id_line: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(Integer, ForeignKey("purchase_orders.id_order", ondelete="CASCADE"), nullable=False, index=True)
    product_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    product_reference: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    product_label: Mapped[str] = mapped_column(String(200), nullable=False)
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    unit_price: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    total_ht: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    order: Mapped[PurchaseOrder] = relationship("PurchaseOrder", back_populates="lines")


class GoodsReceipt(Base):
    __tablename__ = "goods_receipts"

    id_receipt: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    reference: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    order_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("purchase_orders.id_order"), nullable=False
    )
    order_ref: Mapped[str] = mapped_column(String(50), nullable=False)
    product_label: Mapped[str] = mapped_column(String(200), nullable=False)
    quantity_received: Mapped[int] = mapped_column(Integer, nullable=False)
    quantity_expected: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    quality_control_status: Mapped[str] = mapped_column(String(30), nullable=False, default="CONFORME")
    quality_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    received_by_user_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    purchase_order: Mapped[PurchaseOrder] = relationship(
        "PurchaseOrder", back_populates="receipts"
    )


class SupplierInvoice(Base):
    __tablename__ = "supplier_invoices"

    id_invoice: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    invoice_number: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    order_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("purchase_orders.id_order"), nullable=False
    )
    order_ref: Mapped[str] = mapped_column(String(50), nullable=False)
    supplier_name: Mapped[str] = mapped_column(String(200), nullable=False)
    amount_ht: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    vat_rate: Mapped[float] = mapped_column(Float, nullable=False, default=20.0)
    vat_amount: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    amount_ttc: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="VALIDEE", index=True)
    invoice_date: Mapped[date] = mapped_column(Date, default=lambda: datetime.now(timezone.utc).date())
    due_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    paid_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    payment_method: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
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

    purchase_order: Mapped[PurchaseOrder] = relationship(
        "PurchaseOrder", back_populates="invoices"
    )
