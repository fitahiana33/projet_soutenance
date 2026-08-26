from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from app.core.database import Base


class AISimulation(Base):
    __tablename__ = "ai_simulations"

    id_simulation = Column(Integer, primary_key=True, index=True)
    scenario_name = Column(String(150), nullable=False)
    hypothesis = Column(Text, nullable=True)  # e.g., "Augmentation des ventes de 20% + Hausse prix fournisseur de 10%"
    parameters_json = Column(Text, nullable=False)  # JSON input params
    results_json = Column(Text, nullable=False)  # JSON output metrics
    created_by_user_id = Column(Integer, ForeignKey("user_.id_user"), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<AISimulation(id={self.id_simulation}, scenario='{self.scenario_name}')>"
