import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models.roles.role import Role
from app.models.permissions.permission import Permission
from app.schemas.roles.role import RoleCreate, RoleUpdate

logger = logging.getLogger(__name__)


def get_all_roles(db: Session) -> list[Role]:
    try:
        return db.query(Role).all()
    except SQLAlchemyError as e:
        logger.error(f"Error fetching all roles: {e}")
        db.rollback()
        raise e


def get_role_by_id(db: Session, role_id: int) -> Role | None:
    try:
        return db.query(Role).filter(Role.id_role == role_id).first()
    except SQLAlchemyError as e:
        logger.error(f"Error fetching role by ID {role_id}: {e}")
        db.rollback()
        raise e


def create_role(db: Session, role_in: RoleCreate) -> Role:
    try:
        db_role = Role(
            libelle=role_in.libelle,
            description=role_in.description
        )
        if role_in.permission_ids is not None:
            permissions = db.query(Permission).filter(
                Permission.id_permission.in_(role_in.permission_ids)
            ).all()
            db_role.permissions = permissions

        db.add(db_role)
        db.commit()
        db.refresh(db_role)
        return db_role
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error creating role {role_in.libelle}: {e}")
        raise e


def update_role(db: Session, role_id: int, role_in: RoleUpdate) -> Role | None:
    try:
        db_role = get_role_by_id(db, role_id)
        if not db_role:
            return None
        update_data = role_in.model_dump(exclude_unset=True)
        permission_ids = update_data.pop("permission_ids", None)

        for field, value in update_data.items():
            setattr(db_role, field, value)

        if permission_ids is not None:
            permissions = db.query(Permission).filter(
                Permission.id_permission.in_(permission_ids)
            ).all()
            db_role.permissions = permissions

        db.commit()
        db.refresh(db_role)
        return db_role
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error updating role {role_id}: {e}")
        raise e


def assign_role_permissions(db: Session, role_id: int, permission_ids: list[int]) -> Role | None:
    """Affectation directe des permissions à un rôle (Role ↔ Permissions)."""
    try:
        db_role = get_role_by_id(db, role_id)
        if not db_role:
            return None

        permissions = db.query(Permission).filter(
            Permission.id_permission.in_(permission_ids)
        ).all()
        db_role.permissions = permissions

        db.commit()
        db.refresh(db_role)
        return db_role
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error assigning permissions to role {role_id}: {e}")
        raise e


def delete_role(db: Session, role_id: int) -> bool:
    try:
        db_role = get_role_by_id(db, role_id)
        if not db_role:
            return False
        db.delete(db_role)
        db.commit()
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error deleting role {role_id}: {e}")
        raise e
