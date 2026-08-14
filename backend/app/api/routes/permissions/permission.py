import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import require_permission
from app.core.database import get_db
from app.models.users.user import User
from app.schemas.permissions.permission import (
    PermissionCreate,
    PermissionResponse,
    PermissionUpdate
)
from app.services.permissions.permission import (
    create_permission,
    delete_permission,
    get_all_permissions,
    get_permission_by_id,
    update_permission
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/permissions",
    tags=["Permissions"]
)


@router.get(
    "/",
    response_model=list[PermissionResponse],
    summary="Lister toutes les permissions"
)
def list_permissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("ROLE_READ"))
):
    try:
        return get_all_permissions(db)
    except Exception as e:
        logger.error(f"Error in list_permissions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des permissions"
        ) from e


@router.get(
    "/{permission_id}",
    response_model=PermissionResponse,
    summary="Récupérer une permission par ID"
)
def get_permission(
    permission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("ROLE_READ"))
):
    try:
        perm = get_permission_by_id(db, permission_id)
        if not perm:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Permission introuvable"
            )
        return perm
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_permission {permission_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur serveur"
        ) from e


@router.post(
    "/",
    response_model=PermissionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Créer une nouvelle permission"
)
def create_new_permission(
    perm_in: PermissionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("PERMISSION_MANAGE"))
):
    try:
        return create_permission(db, perm_in)
    except Exception as e:
        logger.error(f"Error in create_new_permission: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Impossible de créer la permission"
        ) from e


@router.put(
    "/{permission_id}",
    response_model=PermissionResponse,
    summary="Modifier une permission existante"
)
def update_existing_permission(
    permission_id: int,
    perm_in: PermissionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("PERMISSION_MANAGE"))
):
    try:
        updated = update_permission(db, permission_id, perm_in)
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Permission introuvable"
            )
        return updated
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in update_existing_permission {permission_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la modification de la permission"
        ) from e


@router.delete(
    "/{permission_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Supprimer une permission"
)
def delete_existing_permission(
    permission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("PERMISSION_MANAGE"))
):
    try:
        success = delete_permission(db, permission_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Permission introuvable"
            )
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in delete_existing_permission {permission_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la suppression de la permission"
        ) from e