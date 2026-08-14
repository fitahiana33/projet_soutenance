import logging
import time
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

from app.services.dolibarr.client import dolibarr_client

logger = logging.getLogger(__name__)

# Cache en mémoire de l'état de synchronisation
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
    "history": [],
    "cached_data": {
        "products": [],
        "thirdparties": [],
        "orders": [],
        "invoices": [],
        "users": []
    }
}


async def get_sync_summary() -> Dict[str, Any]:
    """Retourne le résumé complet du module de synchronisation Dolibarr."""
    conn_status = await dolibarr_client.test_connection()

    return {
        "connection": conn_status,
        "last_sync_date": _sync_state["last_sync_date"],
        "periodic_sync_enabled": _sync_state["periodic_sync_enabled"],
        "sync_interval_minutes": _sync_state["sync_interval_minutes"],
        "total_synced_entities": _sync_state["total_synced_entities"]
    }


async def get_sync_history() -> List[Dict[str, Any]]:
    """Retourne l'historique des exécutions de synchronisation."""
    return _sync_state["history"]


async def get_cached_entity_data(entity: str) -> List[Dict[str, Any]]:
    """Retourne les données synchronisées stockées pour une entité spécifique."""
    return _sync_state["cached_data"].get(entity, [])


async def run_synchronization(
    entities: List[str],
    force_full: bool = False,
    triggered_by: str = "Manuel"
) -> Dict[str, Any]:
    """
    Exécute la synchronisation manuelle ou automatique des entités Dolibarr sélectionnées.
    Gère la détection des erreurs et la journalisation.
    """
    start_time = time.time()
    results = []

    target_entities = entities
    if "all" in entities:
        target_entities = ["products", "thirdparties", "orders", "invoices", "users"]

    for entity in target_entities:
        result = await _sync_single_entity(entity, force_full)
        results.append(result)

    duration = round(time.time() - start_time, 2)
    now = datetime.now(timezone.utc)
    _sync_state["last_sync_date"] = now.isoformat()

    has_errors = any(r["status"] == "error" for r in results)
    overall_status = "error" if has_errors else "success"

    log_entry = {
        "id": f"sync_{int(time.time())}",
        "timestamp": now.isoformat(),
        "triggered_by": triggered_by,
        "status": overall_status,
        "duration_seconds": duration,
        "results": results
    }

    _sync_state["history"].insert(0, log_entry)
    # Conserver uniquement les 20 derniers logs
    _sync_state["history"] = _sync_state["history"][:20]

    return log_entry


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

        # En cas d'erreur de connexion, fournir des données de secours mock/cache
        fallback_count = len(_sync_state["cached_data"].get(entity, []))
        return {
            "entity": entity,
            "status": "warning" if fallback_count > 0 else "error",
            "items_fetched": fallback_count,
            "items_synced": fallback_count,
            "errors_count": 1,
            "message": f"Avertissement d'intégration API: {str(e)[:100]}"
        }
