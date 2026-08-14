import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.core.security import (
    create_access_token,
    verify_password
)
from app.services.users.user import (
    get_user_by_email,
    set_last_login
)

logger = logging.getLogger(__name__)


def authenticate_user(
    db: Session,
    email: str,
    password: str
):
    try:
        user = get_user_by_email(db, email)

        if not user:
            return None

        if not verify_password(password, user.password):
            return None

        if not user.is_active:
            return None

        return user
    except SQLAlchemyError as e:
        logger.error(f"Error during authenticate_user for {email}: {e}")
        db.rollback()
        raise e


def login_user(
    db: Session,
    email: str,
    password: str
):
    try:
        user = authenticate_user(db, email, password)

        if not user:
            return None

        set_last_login(db, user)

        token = create_access_token({
            "sub": str(user.id_user),
            "email": user.email
        })

        return token
    except SQLAlchemyError as e:
        logger.error(f"Error during login_user for {email}: {e}")
        db.rollback()
        raise e
