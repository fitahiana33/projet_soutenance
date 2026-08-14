from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings


engine = create_engine(
    settings.database_url,
    pool_pre_ping=True
)


SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False
)


class Base(DeclarativeBase):
    pass


def init_db():
    """Importe les modèles d'authentification et sécurité PostgreSQL puis crée les tables manquantes."""
    from app.models.users.user import User  # noqa: F401
    from app.models.roles.role import Role  # noqa: F401
    from app.models.permissions.permission import Permission  # noqa: F401
    from app.models.authentication.user_role import user_roles  # noqa: F401
    from app.models.authentication.role_permission import role_permissions  # noqa: F401

    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
