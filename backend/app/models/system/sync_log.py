from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime
from app.core.database import Base


class SyncLog(Base):
    __tablename__ = "sync_logs"

    id_sync_log = Column(Integer, primary_key=True, index=True)
    entity_name = Column(String(50), nullable=False, index=True)
    status = Column(String(20), nullable=False, default="SUCCESS")
    started_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    finished_at = Column(DateTime(timezone=True), nullable=True)
    items_fetched = Column(Integer, default=0)
    items_synced = Column(Integer, default=0)
    errors_count = Column(Integer, default=0)
    error_details = Column(Text, nullable=True)
    triggered_by = Column(String(100), default="MANUAL")

    def __repr__(self):
        return f"<SyncLog(id={self.id_sync_log}, entity='{self.entity_name}', status='{self.status}')>"
