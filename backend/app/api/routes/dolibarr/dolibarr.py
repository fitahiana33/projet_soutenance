import logging
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.api.deps import require_permission, get_db
from app.models.users.user import User
from app.schemas.dolibarr.sync import (
    DolibarrConnectionStatusResponse,
    DolibarrSummaryResponse,
    SyncLogResponse,
    SyncRequest
)
from app.services.dolibarr.client import dolibarr_client
from app.services.dolibarr.sync_service import (
    get_cached_entity_data,
    get_sync_history,
    get_sync_summary,
    run_synchronization
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/dolibarr",
    tags=["Dolibarr Integration"]
)


# ============================================================
# CONNECTION TEST & API STATUS
# ============================================================

@router.get(
    "/test-connection",
    response_model=DolibarrConnectionStatusResponse,
    summary="Tester la connexion directe avec l'API Dolibarr"
)
async def test_connection(
    current_user: User = Depends(require_permission("DOLIBARR_READ", "SYSTEM_READ"))
):
    try:
        return await dolibarr_client.test_connection()
    except Exception as e:
        logger.error(f"Error testing Dolibarr connection: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors du test de connexion Dolibarr"
        ) from e


@router.get(
    "/status",
    response_model=DolibarrSummaryResponse,
    summary="Obtenir le statut global du module de synchronisation Dolibarr"
)
async def get_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("DOLIBARR_READ", "SYSTEM_READ"))
):
    try:
        return await get_sync_summary(db)
    except Exception as e:
        logger.error(f"Error getting Dolibarr status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération du statut Dolibarr"
        ) from e


# ============================================================
# MANUAL SYNCHRONIZATION TRIGGER
# ============================================================

@router.post(
    "/sync",
    response_model=SyncLogResponse,
    summary="Déclencher la synchronisation manuelle des données Dolibarr"
)
async def trigger_sync(
    payload: SyncRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("DOLIBARR_SYNC"))
):
    try:
        user_label = f"{current_user.first_name or ''} {current_user.name}".strip() or current_user.email
        return await run_synchronization(
            db=db,
            entities=payload.entities,
            force_full=payload.force_full,
            triggered_by=f"Manuel ({user_label})"
        )
    except Exception as e:
        logger.error(f"Error executing Dolibarr sync: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de l'exécution de la synchronisation Dolibarr"
        ) from e


# ============================================================
# SYNC HISTORY & CACHED DATA
# ============================================================

@router.get(
    "/sync-history",
    response_model=List[SyncLogResponse],
    summary="Consulter l'historique des synchronisations Dolibarr"
)
async def sync_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("DOLIBARR_READ", "SYSTEM_READ"))
):
    try:
        return await get_sync_history(db)
    except Exception as e:
        logger.error(f"Error fetching Dolibarr sync history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération de l'historique de synchronisation"
        ) from e


@router.get(
    "/data/{entity}",
    summary="Consulter les données synchronisées pour une entité spécifique"
)
async def get_entity_data(
    entity: str,
    current_user: User = Depends(require_permission("DOLIBARR_READ", "SYSTEM_READ"))
):
    try:
        if entity not in ["products", "thirdparties", "orders", "invoices", "users"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Entité invalide '{entity}'"
            )

        return await get_cached_entity_data(entity)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching cached entity data for '{entity}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des données de {entity}"
        ) from e
