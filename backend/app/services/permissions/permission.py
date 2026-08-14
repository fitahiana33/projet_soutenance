import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models.permissions.permission import Permission
from app.schemas.permissions.permission import PermissionCreate, PermissionUpdate

logger = logging.getLogger(__name__)


def get_all_permissions(db: Session) -> list[Permission]:
    try:
        return db.query(Permission).all()
    except SQLAlchemyError as e:
        logger.error(f"Error fetching all permissions: {e}")
        db.rollback()
        raise e


def get_permission_by_id(db: Session, permission_id: int) -> Permission | None:
    try:
        return db.query(Permission).filter(Permission.id_permission == permission_id).first()
    except SQLAlchemyError as e:
        logger.error(f"Error fetching permission by ID {permission_id}: {e}")
        db.rollback()
        raise e


def create_permission(db: Session, perm_in: PermissionCreate) -> Permission:
    try:
        db_perm = Permission(
            code=perm_in.code,
            description=perm_in.description
        )
        db.add(db_perm)
        db.commit()
        db.refresh(db_perm)
        return db_perm
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error creating permission {perm_in.code}: {e}")
        raise e


def update_permission(db: Session, permission_id: int, perm_in: PermissionUpdate) -> Permission | None:
    try:
        db_perm = get_permission_by_id(db, permission_id)
        if not db_perm:
            return None
        update_data = perm_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_perm, field, value)
        db.commit()
        db.refresh(db_perm)
        return db_perm
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error updating permission {permission_id}: {e}")
        raise e


def delete_permission(db: Session, permission_id: int) -> bool:
    try:
        db_perm = get_permission_by_id(db, permission_id)
        if not db_perm:
            return False
        db.delete(db_perm)
        db.commit()
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error deleting permission {permission_id}: {e}")
        raise e
