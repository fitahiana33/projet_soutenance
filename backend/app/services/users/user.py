import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.core.security import hash_password
from app.models.roles.role import Role
from app.models.users.user import User

logger = logging.getLogger(__name__)


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
    role_ids: list[int] | None = None
) -> User:
    try:
        user = User(
            name=name,
            first_name=first_name,
            email=email,
            password=hash_password(password),
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        if role_ids is not None:
            roles = db.query(Role).filter(Role.id_role.in_(role_ids)).all()
            user.roles = roles

        db.add(user)
        db.commit()
        db.refresh(user)
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
    role_ids: list[int] | None = None
) -> User:
    try:
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
        return user
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error updating user {user.id_user}: {e}")
        raise e


def assign_user_roles(db: Session, user_id: int, role_ids: list[int]) -> User | None:
    """Affectation directe des rôles à un utilisateur (User ↔ Roles)."""
    try:
        user = get_user_by_id(db, user_id)
        if not user:
            return None

        roles = db.query(Role).filter(Role.id_role.in_(role_ids)).all()
        user.roles = roles
        user.updated_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(user)
        return user
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error assigning roles to user {user_id}: {e}")
        raise e


def set_last_login(db: Session, user: User) -> None:
    try:
        user.last_login_at = datetime.now(timezone.utc)
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error setting last login for user {user.id_user}: {e}")
        raise e


def delete_user(db: Session, user: User) -> None:
    try:
        db.delete(user)
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error deleting user {user.id_user}: {e}")
        raise e
