from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Text, DateTime
from app.core.database import Base


class AIRecommendation(Base):
    __tablename__ = "ai_recommendations"

    id_recommendation = Column(Integer, primary_key=True, index=True)
    module = Column(String(50), nullable=False, index=True)  # "STOCKS", "PURCHASES", "SALES", "RH"
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    action_type = Column(String(100), nullable=False)  # "REORDER", "CHANGE_SUPPLIER", "SAFETY_STOCK_ADJUST"
    priority = Column(String(20), nullable=False, default="MEDIUM")  # "LOW", "MEDIUM", "HIGH", "URGENT"
    impact_score = Column(Float, nullable=True, default=80.0)  # e.g., 85.0 (85%)
    details_json = Column(Text, nullable=True)
    status = Column(String(20), nullable=False, default="PENDING")  # "PENDING", "ACCEPTED", "REJECTED", "EXECUTED"
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<AIRecommendation(id={self.id_recommendation}, title='{self.title}', priority='{self.priority}')>"
