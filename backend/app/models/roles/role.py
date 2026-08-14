from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.authentication.role_permission import role_permissions


class Role(Base):

    __tablename__ = "roles"

    id_role: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    libelle: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    description: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    permissions: Mapped[list["Permission"]] = relationship(
        "Permission",
        secondary=role_permissions
    )
