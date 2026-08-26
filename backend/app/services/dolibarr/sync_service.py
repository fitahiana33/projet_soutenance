import logging
import time
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session

from app.services.dolibarr.client import dolibarr_client
from app.models.system.sync_log import SyncLog

logger = logging.getLogger(__name__)

# Cache en mémoire pour les données d'entités rapides
_sync_state: Dict[str, Any] = {
    "last_sync_date": None,
    "periodic_sync_enabled": True,
    "sync_interval_minutes": 30,
    "total_synced_entities": {
        "products": 0,
        "thirdparties": 0,
        "orders": 0,
        "invoices": 0,
        "users": 0
    },
    "cached_data": {
        "products": [],
        "thirdparties": [],
        "orders": [],
        "invoices": [],
        "users": []
    }
}


async def get_sync_summary(db: Optional[Session] = None) -> Dict[str, Any]:
    """Retourne le résumé complet du module de synchronisation Dolibarr."""
    conn_status = await dolibarr_client.test_connection()
    last_log = None
    if db:
        last_log = db.query(SyncLog).order_by(SyncLog.started_at.desc()).first()

    last_sync_date = last_log.started_at.isoformat() if last_log and last_log.started_at else _sync_state["last_sync_date"]

    return {
        "connection": conn_status,
        "last_sync_date": last_sync_date,
        "periodic_sync_enabled": _sync_state["periodic_sync_enabled"],
        "sync_interval_minutes": _sync_state["sync_interval_minutes"],
        "total_synced_entities": _sync_state["total_synced_entities"]
    }


async def get_sync_history(db: Optional[Session] = None, limit: int = 20) -> List[Dict[str, Any]]:
    """Retourne l'historique des exécutions de synchronisation depuis PostgreSQL sync_logs."""
    if db:
        logs = db.query(SyncLog).order_by(SyncLog.started_at.desc()).limit(limit).all()
        return [
            {
                "id": f"sync_{log.id_sync_log}",
                "id_sync_log": log.id_sync_log,
                "timestamp": log.started_at.isoformat() if log.started_at else None,
                "entity": log.entity_name,
                "status": log.status.lower(),
                "triggered_by": log.triggered_by,
                "items_fetched": log.items_fetched or 0,
                "items_synced": log.items_synced or 0,
                "errors_count": log.errors_count or 0,
                "error_details": log.error_details,
                "duration_seconds": round((log.finished_at - log.started_at).total_seconds(), 2) if log.finished_at and log.started_at else 0.0,
                "results": [
                    {
                        "entity": log.entity_name,
                        "status": log.status.lower(),
                        "items_fetched": log.items_fetched or 0,
                        "items_synced": log.items_synced or 0,
                        "errors_count": log.errors_count or 0,
                        "message": log.error_details or f"Synchronisation {log.entity_name}"
                    }
                ]
            }
            for log in logs
        ]
    return []


async def get_cached_entity_data(entity: str) -> List[Dict[str, Any]]:
    """Retourne les données synchronisées stockées pour une entité spécifique."""
    return _sync_state["cached_data"].get(entity, [])


async def run_synchronization(
    db: Optional[Session],
    entities: List[str],
    force_full: bool = False,
    triggered_by: str = "Manuel"
) -> Dict[str, Any]:
    """
    Exécute la synchronisation manuelle ou automatique des entités Dolibarr sélectionnées.
    Persiste les traces de synchronisation dans la base PostgreSQL (table sync_logs).
    """
    start_time = time.time()
    results = []

    target_entities = entities
    if "all" in entities:
        target_entities = ["products", "thirdparties", "orders", "invoices", "users"]

    for entity in target_entities:
        started_at = datetime.now(timezone.utc)
        result = await _sync_single_entity(entity, force_full)
        finished_at = datetime.now(timezone.utc)
        results.append(result)

        if db:
            try:
                sync_log = SyncLog(
                    entity_name=entity.upper(),
                    status=result["status"].upper(),
                    started_at=started_at,
                    finished_at=finished_at,
                    items_fetched=result.get("items_fetched", 0),
                    items_synced=result.get("items_synced", 0),
                    errors_count=result.get("errors_count", 0),
                    error_details=result.get("message") if result["status"] != "success" else None,
                    triggered_by=triggered_by
                )
                db.add(sync_log)
                db.commit()
            except Exception as e:
                db.rollback()
                logger.error(f"Erreur enregistrement log de synchronisation: {e}")

    duration = round(time.time() - start_time, 2)
    now = datetime.now(timezone.utc)
    _sync_state["last_sync_date"] = now.isoformat()

    has_errors = any(r["status"] == "error" for r in results)
    overall_status = "error" if has_errors else "success"

    return {
        "id": f"sync_{int(time.time())}",
        "timestamp": now.isoformat(),
        "triggered_by": triggered_by,
        "status": overall_status,
        "duration_seconds": duration,
        "results": results
    }


async def _sync_single_entity(entity: str, force_full: bool) -> Dict[str, Any]:
    """Exécute la synchronisation pour une entité spécifique avec gestion des erreurs."""
    try:
        data = []
        if entity == "products":
            data = await dolibarr_client.get_products()
        elif entity == "thirdparties":
            data = await dolibarr_client.get_thirdparties()
        elif entity == "orders":
            data = await dolibarr_client.get_orders()
        elif entity == "invoices":
            data = await dolibarr_client.get_invoices()
        elif entity == "users":
            data = await dolibarr_client.get_users()
        else:
            return {
                "entity": entity,
                "status": "error",
                "items_fetched": 0,
                "items_synced": 0,
                "errors_count": 1,
                "message": f"Entité inconnue '{entity}'"
            }

        count = len(data)
        _sync_state["cached_data"][entity] = data
        _sync_state["total_synced_entities"][entity] = count

        return {
            "entity": entity,
            "status": "success",
            "items_fetched": count,
            "items_synced": count,
            "errors_count": 0,
            "message": f"Synchronisation réussie ({count} éléments)"
        }
    except Exception as e:
        logger.error(f"Error syncing Dolibarr entity '{entity}': {e}")

        fallback_count = len(_sync_state["cached_data"].get(entity, []))
        return {
            "entity": entity,
            "status": "warning" if fallback_count > 0 else "error",
            "items_fetched": fallback_count,
            "items_synced": fallback_count,
            "errors_count": 1,
            "message": f"Avertissement d'intégration API: {str(e)[:100]}"
        }
