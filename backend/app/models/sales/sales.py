from datetime import datetime, timezone, date
from typing import Optional, List
from sqlalchemy import (
    Integer, String, Float, Boolean, DateTime, Date, ForeignKey, Text
)
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.core.database import Base


class Customer(Base):
    __tablename__ = "customers"

    id_customer: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    dolibarr_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    code_client: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    email: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    country: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    tax_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="ACTIF")
    payment_terms: Mapped[str] = mapped_column(String(50), nullable=False, default="30_DAYS")
    payment_terms_days: Mapped[int] = mapped_column(Integer, nullable=False, default=30)
    total_revenue_generated: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    credit_limit: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    orders: Mapped[List["SalesOrder"]] = relationship("SalesOrder", back_populates="customer")


class SalesQuote(Base):
    __tablename__ = "sales_quotes"

    id_quote: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    reference: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    customer_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("customers.id_customer"), nullable=False
    )
    customer_name: Mapped[str] = mapped_column(String(200), nullable=False)
    title: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    items_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    total_ht: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    vat_rate: Mapped[float] = mapped_column(Float, nullable=False, default=20.0)
    vat_amount: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    total_ttc: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    discount_percent: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="DRAFT", index=True)
    quote_date: Mapped[date] = mapped_column(Date, default=lambda: datetime.now(timezone.utc).date())
    validity_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    accepted_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
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

    customer: Mapped[Customer] = relationship("Customer")


class SalesOrder(Base):
    __tablename__ = "sales_orders"

    id_order: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    reference: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    quote_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    customer_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("customers.id_customer"), nullable=False
    )
    customer_name: Mapped[str] = mapped_column(String(200), nullable=False)
    items_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    total_ht: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    vat_rate: Mapped[float] = mapped_column(Float, nullable=False, default=20.0)
    vat_amount: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    total_ttc: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    discount_percent: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="CONFIRMEE", index=True)
    order_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    expected_delivery_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    actual_delivery_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    shipping_address: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    billing_address: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
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

    customer: Mapped[Customer] = relationship("Customer", back_populates="orders")
    deliveries: Mapped[List["Delivery"]] = relationship("Delivery", back_populates="sales_order")
    invoices: Mapped[List["SalesInvoice"]] = relationship("SalesInvoice", back_populates="sales_order")
    lines: Mapped[List["SalesOrderLine"]] = relationship(
        "SalesOrderLine", back_populates="order", cascade="all, delete-orphan"
    )


class SalesOrderLine(Base):
    __tablename__ = "sales_order_lines"

    id_line: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(Integer, ForeignKey("sales_orders.id_order", ondelete="CASCADE"), nullable=False, index=True)
    product_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    product_reference: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    product_label: Mapped[str] = mapped_column(String(200), nullable=False)
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    unit_price: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    discount_percent: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    total_ht: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    order: Mapped[SalesOrder] = relationship("SalesOrder", back_populates="lines")


class Delivery(Base):
    __tablename__ = "deliveries"

    id_delivery: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    reference: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    order_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("sales_orders.id_order"), nullable=False
    )
    order_ref: Mapped[str] = mapped_column(String(50), nullable=False)
    customer_name: Mapped[str] = mapped_column(String(200), nullable=False)
    items_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    total_quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="PREPAREE", index=True)
    delivery_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    tracking_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    carrier: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    delivered_by_user_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    customer_signature: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    sales_order: Mapped[SalesOrder] = relationship("SalesOrder", back_populates="deliveries")


class SalesInvoice(Base):
    __tablename__ = "sales_invoices"

    id_invoice: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    invoice_number: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    order_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("sales_orders.id_order"), nullable=False
    )
    order_ref: Mapped[str] = mapped_column(String(50), nullable=False)
    customer_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    customer_name: Mapped[str] = mapped_column(String(200), nullable=False)
    items_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    total_ht: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    vat_rate: Mapped[float] = mapped_column(Float, nullable=False, default=20.0)
    vat_amount: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    total_ttc: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    discount_percent: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    amount_paid: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="VALIDEE", index=True)
    invoice_date: Mapped[date] = mapped_column(Date, default=lambda: datetime.now(timezone.utc).date())
    due_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    paid_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    payment_method: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    payment_ref: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
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

    sales_order: Mapped[SalesOrder] = relationship("SalesOrder", back_populates="invoices")

    @property
    def remaining_amount(self) -> float:
        return max(0.0, self.total_ttc - self.amount_paid)

    @property
    def is_paid(self) -> bool:
        return self.amount_paid >= self.total_ttc and self.total_ttc > 0
