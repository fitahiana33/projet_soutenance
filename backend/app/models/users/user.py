from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.authentication.user_role import user_roles


class User(Base):

    __tablename__ = "user_"

    id_user: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    name: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    first_name: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    email: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True
    )

    password: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    is_active: Mapped[bool | None] = mapped_column(
        Boolean,
        nullable=True
    )

    created_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    roles: Mapped[list["Role"]] = relationship(
        "Role",
        secondary=user_roles,
        backref="users"
    )
