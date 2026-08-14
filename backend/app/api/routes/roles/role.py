import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import require_permission
from app.core.database import get_db
from app.models.users.user import User
from app.schemas.roles.role import (
    RoleCreate,
    RolePermissionAssign,
    RoleResponse,
    RoleUpdate
)
from app.services.roles.role import (
    assign_role_permissions,
    create_role,
    delete_role,
    get_all_roles,
    get_role_by_id,
    update_role
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/roles",
    tags=["Roles"]
)


@router.get(
    "/",
    response_model=list[RoleResponse],
    summary="Lister tous les rôles"
)
def list_roles(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("ROLE_READ"))
):
    try:
        return get_all_roles(db)
    except Exception as e:
        logger.error(f"Error in list_roles: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des rôles"
        ) from e


@router.get(
    "/{role_id}",
    response_model=RoleResponse,
    summary="Récupérer un rôle par ID"
)
def get_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("ROLE_READ"))
):
    try:
        role = get_role_by_id(db, role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rôle introuvable"
            )
        return role
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_role {role_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur serveur"
        ) from e


@router.post(
    "/",
    response_model=RoleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Créer un nouveau rôle"
)
def create_new_role(
    role_in: RoleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("ROLE_MANAGE"))
):
    try:
        return create_role(db, role_in)
    except Exception as e:
        logger.error(f"Error in create_new_role: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Impossible de créer le rôle"
        ) from e


@router.put(
    "/{role_id}",
    response_model=RoleResponse,
    summary="Modifier un rôle existant"
)
def update_existing_role(
    role_id: int,
    role_in: RoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("ROLE_MANAGE"))
):
    try:
        updated = update_role(db, role_id, role_in)
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rôle introuvable"
            )
        return updated
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in update_existing_role {role_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la modification du rôle"
        ) from e


@router.post(
    "/{role_id}/permissions",
    response_model=RoleResponse,
    summary="Affecter des permissions à un rôle (Role ↔ Permissions)"
)
def assign_permissions(
    role_id: int,
    payload: RolePermissionAssign,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("ROLE_MANAGE"))
):
    try:
        role = assign_role_permissions(db, role_id, payload.permission_ids)
        if role is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rôle introuvable"
            )
        return role
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error assigning permissions to role {role_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de l'affectation des permissions"
        ) from e


@router.delete(
    "/{role_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Supprimer un rôle"
)
def delete_existing_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("ROLE_MANAGE"))
):
    try:
        success = delete_role(db, role_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rôle introuvable"
            )
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in delete_existing_role {role_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la suppression du rôle"
        ) from e