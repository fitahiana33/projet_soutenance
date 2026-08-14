import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.api.deps import require_permission
from app.core.database import get_db
from app.models.users.user import User
from app.schemas.users.user import (
    UserCreate,
    UserResponse,
    UserRoleAssign,
    UserUpdate
)
from app.services.users.user import (
    assign_user_roles,
    create_user,
    delete_user,
    get_all_users,
    get_user_by_email,
    get_user_by_id,
    update_user
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


# ============================================================
# GET ALL USERS (WITH SEARCH & FILTERING)
# ============================================================

@router.get(
    "/",
    response_model=list[UserResponse],
    summary="Lister, rechercher et filtrer les utilisateurs"
)
def list_users(
    q: Optional[str] = Query(None, description="Recherche par nom, prénom ou email"),
    role_id: Optional[int] = Query(None, description="Filtrer par ID de rôle"),
    is_active: Optional[bool] = Query(None, description="Filtrer par statut actif/inactif"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("USER_READ"))
):
    try:
        users = get_all_users(db)

        # Filtrage applicatif en mémoire (ou query builder)
        if q:
            term = q.lower()
            users = [
                u for u in users
                if (u.name and term in u.name.lower())
                or (u.first_name and term in u.first_name.lower())
                or (u.email and term in u.email.lower())
            ]

        if role_id is not None:
            users = [
                u for u in users
                if any(r.id_role == role_id for r in u.roles)
            ]

        if is_active is not None:
            users = [u for u in users if u.is_active == is_active]

        return users
    except Exception as e:
        logger.error(f"Error listing users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des utilisateurs"
        ) from e


# ============================================================
# GET USER BY ID
# ============================================================

@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Récupérer un utilisateur par ID"
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("USER_READ"))
):
    try:
        user = get_user_by_id(db, user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utilisateur introuvable"
            )
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur serveur"
        ) from e


# ============================================================
# CREATE USER
# ============================================================

@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Créer un nouvel utilisateur"
)
def create_new_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("USER_CREATE"))
):
    try:
        existing_user = get_user_by_email(db, user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cette adresse email est déjà utilisée"
            )

        return create_user(
            db=db,
            name=user_data.name,
            first_name=user_data.first_name,
            email=user_data.email,
            password=user_data.password,
            role_ids=user_data.role_ids
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la création de l'utilisateur"
        ) from e


# ============================================================
# UPDATE USER
# ============================================================

@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="Modifier un utilisateur"
)
def update_existing_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("USER_UPDATE"))
):
    try:
        user = get_user_by_id(db, user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utilisateur introuvable"
            )

        if user_data.email is not None:
            existing_user = get_user_by_email(db, user_data.email)
            if existing_user and existing_user.id_user != user_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Cette adresse email est déjà utilisée"
                )

        return update_user(
            db=db,
            user=user,
            name=user_data.name,
            first_name=user_data.first_name,
            email=user_data.email,
            password=user_data.password,
            is_active=user_data.is_active,
            role_ids=user_data.role_ids
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la modification de l'utilisateur"
        ) from e


# ============================================================
# TOGGLE USER STATUS (DÉSACTIVATION / RÉACTIVATION)
# ============================================================

@router.patch(
    "/{user_id}/status",
    response_model=UserResponse,
    summary="Activer ou désactiver un utilisateur"
)
def toggle_user_status(
    user_id: int,
    is_active: bool,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("USER_UPDATE"))
):
    try:
        user = get_user_by_id(db, user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utilisateur introuvable"
            )

        return update_user(db=db, user=user, is_active=is_active)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error toggling status for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors du changement de statut"
        ) from e


# ============================================================
# ASSIGN ROLES TO USER (User ↔ Roles)
# ============================================================

@router.post(
    "/{user_id}/roles",
    response_model=UserResponse,
    summary="Affecter des rôles à un utilisateur (User ↔ Roles)"
)
def assign_roles(
    user_id: int,
    payload: UserRoleAssign,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("USER_ASSIGN_ROLE"))
):
    try:
        user = assign_user_roles(db, user_id, payload.role_ids)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utilisateur introuvable"
            )
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error assigning roles to user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de l'affectation des rôles"
        ) from e


# ============================================================
# DELETE USER
# ============================================================

@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Supprimer un utilisateur"
)
def delete_existing_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("USER_DELETE"))
):
    try:
        user = get_user_by_id(db, user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utilisateur introuvable"
            )

        delete_user(db, user)
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la suppression"
        ) from e
