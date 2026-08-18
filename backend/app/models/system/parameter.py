from datetime import datetime, timezone
from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class SystemParameter(Base):
    __tablename__ = "system_parameter"

    id_param: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    category: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="GENERAL"
    )

    key: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True
    )

    value: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    label: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    description: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )
