import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import require_active_user
from app.core.database import get_db
from app.core.security import verify_password, hash_password
from app.models.users.user import User
from app.schemas.authentication.login import (
    LoginRequest,
    PasswordChangeRequest,
    TokenResponse
)
from app.schemas.users.user import UserResponse
from app.services.authentication.auth import login_user

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Authentifier un utilisateur"
)
def login(
    credentials: LoginRequest,
    db: Session = Depends(get_db)
):
    try:
        token = login_user(
            db,
            credentials.email,
            credentials.password
        )

        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou mot de passe incorrect"
            )

        return {
            "access_token": token,
            "token_type": "bearer"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in login endpoint for {credentials.email}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur serveur lors de la connexion"
        ) from e


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Récupérer l'utilisateur courant"
)
def me(
    user: User = Depends(require_active_user)
):
    try:
        return user
    except Exception as e:
        logger.error(f"Error in /auth/me endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur serveur"
        ) from e


@router.post(
    "/change-password",
    summary="Changer le mot de passe de l'utilisateur courant"
)
def change_password(
    payload: PasswordChangeRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_active_user)
):
    try:
        if not verify_password(payload.old_password, user.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ancien mot de passe incorrect"
            )

        user.password = hash_password(payload.new_password)
        db.commit()
        return {"message": "Mot de passe mis à jour avec succès"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error changing password for user {user.id_user}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur serveur lors de la modification du mot de passe"
        ) from e
