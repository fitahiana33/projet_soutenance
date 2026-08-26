import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.audit.audit_log import AuditLog

logger = logging.getLogger(__name__)


def log_action(
    db: Session,
    action: str,
    module: str,
    user_id: Optional[int] = None,
    username: str = "SYSTEM",
    user_role: Optional[str] = None,
    target_entity: Optional[str] = None,
    details: Optional[str] = None,
    old_values: Optional[Dict[str, Any]] = None,
    new_values: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None
) -> AuditLog:
    """Enregistre un événement dans le journal d'audit (table audit_logs en PostgreSQL)."""
    try:
        log_entry = AuditLog(
            user_id=user_id,
            username=username,
            user_role=user_role,
            action=action.upper(),
            module=module.upper(),
            target_entity=target_entity,
            details=details,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
            created_at=datetime.now(timezone.utc)
        )
        db.add(log_entry)
        db.commit()
        db.refresh(log_entry)
        return log_entry
    except Exception as e:
        db.rollback()
        logger.error(f"Erreur lors de l'enregistrement du log d'audit: {e}")
        return None


def get_audit_logs(
    db: Session,
    module: Optional[str] = None,
    action: Optional[str] = None,
    username: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
) -> List[Dict[str, Any]]:
    """Récupère les logs d'audit filtrés et triés par date décroissante."""
    query = db.query(AuditLog)
    
    if module:
        mod_upper = module.upper()
        if mod_upper in ["SYSTEME", "SYSTEM"]:
            query = query.filter(AuditLog.module.in_(["SYSTEM", "SYSTEME"]))
        else:
            query = query.filter(AuditLog.module == mod_upper)

    if action:
        query = query.filter(AuditLog.action == action.upper())
    if username:
        query = query.filter(AuditLog.username.ilike(f"%{username}%"))

    logs = query.order_by(AuditLog.created_at.desc()).offset(offset).limit(limit).all()

    result = []
    for l in logs:
        result.append({
            "id_audit": l.id_audit,
            "user_id": l.user_id,
            "username": l.username,
            "user_role": l.user_role,
            "action": l.action,
            "module": l.module,
            "target_entity": l.target_entity,
            "details": l.details,
            "old_values": l.old_values,
            "new_values": l.new_values,
            "ip_address": l.ip_address,
            "created_at": l.created_at.isoformat() if l.created_at else None
        })
    return result


def get_audit_stats(db: Session) -> Dict[str, Any]:
    """Synthèse des statistiques d'audit pour le tableau de bord de sécurité."""
    total_logs = db.query(AuditLog).count()
    
    # Répartition par module
    modules = ["ACHATS", "VENTES", "STOCKS", "RH", "USERS", "ROLES", "SYSTEM"]
    by_module = {}
    for m in modules:
        by_module[m] = db.query(AuditLog).filter(AuditLog.module == m).count()

    # Répartition par action
    actions = ["CREATE", "UPDATE", "DELETE", "PURGE", "LOGIN", "VALIDATE"]
    actions_count = {}
    for act in actions:
        actions_count[act] = db.query(AuditLog).filter(AuditLog.action == act).count()

    # Dernières actions sensibles
    recent_sensitive = (
        db.query(AuditLog)
        .filter(AuditLog.action.in_(["DELETE", "PURGE", "UPDATE_ROLE", "VALIDATE_PAIE"]))
        .order_by(AuditLog.created_at.desc())
        .limit(5)
        .all()
    )

    return {
        "total_logs": total_logs,
        "total_audit_events": total_logs,
        "actions_count": actions_count,
        "events_by_module": by_module,
        "recent_sensitive_events_count": len(recent_sensitive)
    }
