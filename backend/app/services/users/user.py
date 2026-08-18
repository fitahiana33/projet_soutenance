import logging
from typing import Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.core.security import hash_password
from app.models.roles.role import Role
from app.models.users.user import User
from app.services.audit.audit_service import log_action

logger = logging.getLogger(__name__)


def _role_labels(roles) -> list[str]:
    return [r.libelle for r in roles] if roles else []


def get_all_users(db: Session) -> list[User]:
    try:
        return db.query(User).all()
    except SQLAlchemyError as e:
        logger.error(f"Error fetching all users: {e}")
        db.rollback()
        raise e


def get_user_by_id(db: Session, user_id: int) -> User | None:
    try:
        return db.query(User).filter(User.id_user == user_id).first()
    except SQLAlchemyError as e:
        logger.error(f"Error fetching user by ID {user_id}: {e}")
        db.rollback()
        raise e


def get_user_by_email(db: Session, email: str) -> User | None:
    try:
        return db.query(User).filter(User.email == email).first()
    except SQLAlchemyError as e:
        logger.error(f"Error fetching user by email {email}: {e}")
        db.rollback()
        raise e


def create_user(
    db: Session,
    name: str,
    first_name: str | None,
    email: str,
    password: str,
    role_ids: list[int] | None = None,
    actor_user: Optional[User] = None
) -> User:
    try:
        roles = []
        if role_ids is not None:
            roles = db.query(Role).filter(Role.id_role.in_(role_ids)).all()

        user = User(
            name=name,
            first_name=first_name,
            email=email,
            password=hash_password(password),
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            roles=roles
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        new_values = {
            "id_user": user.id_user,
            "name": user.name,
            "first_name": user.first_name,
            "email": user.email,
            "is_active": user.is_active,
            "roles": _role_labels(user.roles)
        }
        log_action(
            db,
            action="CREATE",
            module="USERS",
            user_id=actor_user.id_user if actor_user else None,
            username=actor_user.email if actor_user else "SYSTEM",
            user_role=_role_labels(actor_user.roles)[0] if actor_user and actor_user.roles else None,
            target_entity=f"USER:{user.id_user}",
            details=f"Création utilisateur {user.email}",
            new_values=new_values
        )
        return user
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error creating user {email}: {e}")
        raise e


def update_user(
    db: Session,
    user: User,
    name: str | None = None,
    first_name: str | None = None,
    email: str | None = None,
    password: str | None = None,
    is_active: bool | None = None,
    role_ids: list[int] | None = None,
    actor_user: Optional[User] = None
) -> User:
    try:
        old_values = {
            "name": user.name,
            "first_name": user.first_name,
            "email": user.email,
            "is_active": user.is_active,
            "roles": _role_labels(user.roles)
        }

        if name is not None:
            user.name = name
        if first_name is not None:
            user.first_name = first_name
        if email is not None:
            user.email = email
        if password is not None:
            user.password = hash_password(password)
        if is_active is not None:
            user.is_active = is_active
        if role_ids is not None:
            roles = db.query(Role).filter(Role.id_role.in_(role_ids)).all()
            user.roles = roles

        user.updated_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(user)

        new_values = {
            "name": user.name,
            "first_name": user.first_name,
            "email": user.email,
            "is_active": user.is_active,
            "roles": _role_labels(user.roles)
        }
        if password is not None:
            old_values["password_changed"] = False
            new_values["password_changed"] = True

        changes = {k: (old_values.get(k), new_values.get(k)) for k in set(list(old_values.keys()) + list(new_values.keys())) if old_values.get(k) != new_values.get(k)}

        log_action(
            db,
            action="UPDATE",
            module="USERS",
            user_id=actor_user.id_user if actor_user else None,
            username=actor_user.email if actor_user else "SYSTEM",
            user_role=_role_labels(actor_user.roles)[0] if actor_user and actor_user.roles else None,
            target_entity=f"USER:{user.id_user}",
            details=f"Modification utilisateur {user.email} - champs modifiés: {list(changes.keys())}",
            old_values=old_values,
            new_values=new_values
        )
        return user
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error updating user {user.id_user}: {e}")
        raise e


def assign_user_roles(
    db: Session,
    user_id: int,
    role_ids: list[int],
    actor_user: Optional[User] = None
) -> User | None:
    """Affectation directe des rôles à un utilisateur (User ↔ Roles)."""
    try:
        user = get_user_by_id(db, user_id)
        if not user:
            return None

        old_values = {"user_id": user_id, "roles": _role_labels(user.roles)}

        roles = db.query(Role).filter(Role.id_role.in_(role_ids)).all()
        user.roles = roles
        user.updated_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(user)

        log_action(
            db,
            action="UPDATE_ROLE",
            module="USERS",
            user_id=actor_user.id_user if actor_user else None,
            username=actor_user.email if actor_user else "SYSTEM",
            user_role=_role_labels(actor_user.roles)[0] if actor_user and actor_user.roles else None,
            target_entity=f"USER:{user.id_user}",
            details=f"Affectation rôles pour {user.email}: {_role_labels(user.roles)}",
            old_values=old_values,
            new_values={"user_id": user_id, "roles": _role_labels(user.roles)}
        )
        return user
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error assigning roles to user {user_id}: {e}")
        raise e


def set_last_login(db: Session, user: User) -> None:
    try:
        was = user.last_login_at
        user.last_login_at = datetime.now(timezone.utc)
        db.commit()
        log_action(
            db,
            action="LOGIN",
            module="AUTH",
            user_id=user.id_user,
            username=user.email,
            user_role=_role_labels(user.roles)[0] if user.roles else None,
            target_entity=f"USER:{user.id_user}",
            details=f"Connexion de {user.email} (précédente: {was.isoformat() if was else 'jamais'})"
        )
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error setting last login for user {user.id_user}: {e}")
        raise e


def delete_user(
    db: Session,
    user: User,
    actor_user: Optional[User] = None
) -> None:
    try:
        old_values = {
            "id_user": user.id_user,
            "name": user.name,
            "first_name": user.first_name,
            "email": user.email,
            "is_active": user.is_active,
            "roles": _role_labels(user.roles)
        }
        db.delete(user)
        db.commit()

        log_action(
            db,
            action="DELETE",
            module="USERS",
            user_id=actor_user.id_user if actor_user else None,
            username=actor_user.email if actor_user else "SYSTEM",
            user_role=_role_labels(actor_user.roles)[0] if actor_user and actor_user.roles else None,
            target_entity=f"USER:{old_values['id_user']}",
            details=f"Suppression utilisateur {old_values['email']}",
            old_values=old_values
        )
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error deleting user {user.id_user}: {e}")
        raise e
