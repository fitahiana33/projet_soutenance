from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Text, DateTime
from app.core.database import Base


class AIAnomaly(Base):
    __tablename__ = "ai_anomalies"

    id_anomaly = Column(Integer, primary_key=True, index=True)
    module = Column(String(50), nullable=False, index=True)  # e.g., "PURCHASES", "STOCKS", "SALES", "PAYROLL"
    entity_type = Column(String(50), nullable=False)  # e.g., "SUPPLIER_PRICE", "CONSUMPTION", "OVERTIME"
    entity_id = Column(Integer, nullable=True)
    anomaly_type = Column(String(100), nullable=False)
    severity = Column(String(20), nullable=False, default="WARNING")  # "INFO", "WARNING", "CRITICAL"
    expected_value = Column(Float, nullable=True)
    actual_value = Column(Float, nullable=True)
    deviation_percent = Column(Float, nullable=True)
    details_json = Column(Text, nullable=True)
    status = Column(String(20), nullable=False, default="DETECTED")  # "DETECTED", "REVIEWED", "RESOLVED", "IGNORED"
    detected_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<AIAnomaly(id={self.id_anomaly}, module='{self.module}', severity='{self.severity}')>"
