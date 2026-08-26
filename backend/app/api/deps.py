from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token, InvalidCredentialsError
from app.models.users.user import User
from app.services.users.user import get_user_by_id


bearer_scheme = HTTPBearer(
    auto_error=False,
    description="Token JWT requis"
)


def get_current_user(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> User:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentification requise",
            headers={"WWW-Authenticate": "Bearer"}
        )

    try:
        payload = decode_access_token(credentials.credentials)
        user_id = payload.get("sub")
        if user_id is None:
            raise InvalidCredentialsError("Payload invalide")
    except InvalidCredentialsError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide ou expiré",
            headers={"WWW-Authenticate": "Bearer"}
        ) from exc

    try:
        user = get_user_by_id(db, int(user_id))
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide ou expiré",
            headers={"WWW-Authenticate": "Bearer"}
        )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide ou expiré",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return user


def require_active_user(
    user: User = Depends(get_current_user),
) -> User:
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Votre compte est désactivé"
        )

    return user


def _normalize(code: str) -> str:
    return code.upper().replace(":", "_").replace("-", "_")


def require_role(*role_names: str):
    def dependency(user: User = Depends(get_current_user)) -> User:
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Votre compte est désactivé"
            )

        user_role_names = {role.libelle.upper() for role in user.roles}
        target_role_names = {r.upper() for r in role_names}

        # ADMIN a tous les privilèges de rôle
        if "ADMIN" in user_role_names or user_role_names.intersection(target_role_names):
            return user

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès refusé : rôle insuffisant"
        )

    return dependency


def require_permission(*permission_codes: str):
    def dependency(user: User = Depends(get_current_user)) -> User:
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Votre compte est désactivé"
            )

        user_role_names = {role.libelle.upper() for role in user.roles}
        # L'administrateur système possède toutes les permissions
        if "ADMIN" in user_role_names:
            return user

        user_permissions = {
            _normalize(permission.code)
            for role in user.roles
            for permission in role.permissions
        }

        normalized_targets = {_normalize(code) for code in permission_codes}

        if not user_permissions.intersection(normalized_targets):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accès refusé : permission insuffisante"
            )

        return user

    return dependency


def require_all_permissions(*permission_codes: str):
    def dependency(user: User = Depends(get_current_user)) -> User:
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Votre compte est désactivé"
            )

        user_role_names = {role.libelle.upper() for role in user.roles}
        if "ADMIN" in user_role_names:
            return user

        user_permissions = {
            _normalize(permission.code)
            for role in user.roles
            for permission in role.permissions
        }

        normalized_targets = {_normalize(code) for code in permission_codes}

        if not normalized_targets.issubset(user_permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accès refusé : permissions cumulatives insuffisantes"
            )

        return user

    return dependency
