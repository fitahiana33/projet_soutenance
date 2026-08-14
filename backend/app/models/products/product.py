from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class Category(Base):
    __tablename__ = "categories"

    id_category = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(String(255), nullable=True)

    products = relationship("Product", back_populates="category")


class Product(Base):
    __tablename__ = "products"

    id_product = Column(Integer, primary_key=True, index=True)
    reference = Column(String(50), nullable=False, unique=True, index=True)  # SKU / Code produit
    label = Column(String(150), nullable=False, index=True)
    description = Column(Text, nullable=True)

    category_id = Column(Integer, ForeignKey("categories.id_category"), nullable=True)
    category = relationship("Category", back_populates="products")

    price_purchase = Column(Float, nullable=False, default=0.0)  # Prix d'achat HT
    price_sell = Column(Float, nullable=False, default=0.0)      # Prix de vente HT

    status = Column(String(20), nullable=False, default="ACTIF")  # ACTIF, INACTIF, REAPPRO

    stock_quantity = Column(Integer, nullable=False, default=0)   # Stock total physique
    stock_reserved = Column(Integer, nullable=False, default=0)   # Stock réservé commandes
    stock_min = Column(Integer, nullable=False, default=5)        # Seuil d'alerte stock min
    stock_max = Column(Integer, nullable=False, default=100)      # Capacité stock max

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    movements = relationship("StockMovement", back_populates="product", cascade="all, delete-orphan")

    @property
    def stock_available((self)) -> int:
        """Calcule le stock net réellement disponible (Physique - Réservé)."""
        return max(0, (self.stock_quantity or 0) - (self.stock_reserved or 0))


class StockMovement(Base):
    __tablename__ = "stock_movements"

    id_movement = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id_product"), nullable=False)
    product = relationship("Product", back_populates="movements")

    movement_type = Column(String(20), nullable=False)  # ENTREE, SORTIE, AJUSTEMENT, TRANSFERT
    quantity = Column(Integer, nullable=False)
    reference_doc = Column(String(100), nullable=True)  # N° Bon de livraison / commande
    comment = Column(String(255), nullable=True)

    created_by_user_id = Column(Integer, ForeignKey("user_.id_user"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
