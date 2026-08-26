from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.users.user import User
from app.api.deps import require_permission
from app.services.audit.audit_service import get_audit_logs, get_audit_stats

router = APIRouter(prefix="/audit", tags=["Audit & Traçabilité des Actions"])


@router.get(
    "/logs",
    summary="Consulter le journal d'audit de sécurité et traçabilité"
)
async def read_audit_logs(
    module: Optional[str] = Query(None, description="Filtrer par module: ACHATS, VENTES, STOCKS, RH, USERS, ROLES, SYSTEM"),
    action: Optional[str] = Query(None, description="Filtrer par action: CREATE, UPDATE, DELETE, LOGIN, PURGE"),
    username: Optional[str] = Query(None, description="Filtrer par nom d'utilisateur"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("AUDIT_READ"))
):
    return get_audit_logs(db, module=module, action=action, username=username, limit=limit, offset=offset)


@router.get(
    "/stats",
    summary="Statistiques du journal d'audit"
)
async def read_audit_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("AUDIT_READ"))
):
    return get_audit_stats(db)
