from datetime import datetime, date, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, Date
from app.core.database import Base


class AnalyticsSnapshot(Base):
    __tablename__ = "analytics_snapshots"

    id_snapshot = Column(Integer, primary_key=True, index=True)
    snapshot_date = Column(Date, nullable=False, default=date.today, index=True)
    metric_category = Column(String(50), nullable=False, index=True)  # "SALES", "STOCKS", "PURCHASES", "HR", "GLOBAL"
    metrics_json = Column(Text, nullable=False)  # Stored JSON object containing daily KPIs
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<AnalyticsSnapshot(id={self.id_snapshot}, date='{self.snapshot_date}', cat='{self.metric_category}')>"
