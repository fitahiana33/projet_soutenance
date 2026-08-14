from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class DolibarrConnectionStatusResponse(BaseModel):
    connected: bool
    base_url: str
    message: str
    version: Optional[str] = None
    response_time_ms: Optional[float] = None


class SyncRequest(BaseModel):
    entities: List[str] = Field(
        default=["products", "thirdparties", "orders", "invoices", "users"],
        description="Liste des entités à synchroniser: products, thirdparties, orders, invoices, users, or all"
    )
    force_full: bool = Field(
        default=False,
        description="Si True, ignore la date de dernière sync et fait un import complet"
    )


class EntitySyncResult(BaseModel):
    entity: str
    status: str  # 'success', 'warning', 'error'
    items_fetched: int
    items_synced: int
    errors_count: int
    message: str


class SyncLogResponse(BaseModel):
    id: str
    timestamp: datetime
    triggered_by: str
    status: str
    duration_seconds: float
    results: List[EntitySyncResult]


class DolibarrSummaryResponse(BaseModel):
    connection: DolibarrConnectionStatusResponse
    last_sync_date: Optional[datetime] = None
    periodic_sync_enabled: bool = True
    sync_interval_minutes: int = 30
    total_synced_entities: Dict[str, int] = Field(
        default_factory=lambda: {
            "products": 0,
            "thirdparties": 0,
            "orders": 0,
            "invoices": 0,
            "users": 0
        }
    )
