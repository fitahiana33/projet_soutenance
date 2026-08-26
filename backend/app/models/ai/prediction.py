from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Text, DateTime
from app.core.database import Base


class AIPrediction(Base):
    __tablename__ = "ai_predictions"

    id_prediction = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String(50), nullable=False, index=True)  # e.g., "PRODUCT", "STOCK", "SALE", "HR"
    entity_id = Column(Integer, nullable=True, index=True)
    prediction_type = Column(String(100), nullable=False, index=True)  # e.g., "STOCK_OUT_RISK", "DEMAND_FORECAST"
    predicted_value = Column(Float, nullable=False)
    unit = Column(String(20), nullable=True, default="units")
    confidence_score = Column(Float, nullable=False, default=0.95)  # e.g., 0.88 (88%)
    factors_json = Column(Text, nullable=True)  # JSON explanation of factors
    horizon_days = Column(Integer, nullable=True, default=30)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<AIPrediction(id={self.id_prediction}, type='{self.prediction_type}', val={self.predicted_value})>"
