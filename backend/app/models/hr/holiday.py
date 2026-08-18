from datetime import date, datetime, timezone
from sqlalchemy import Boolean, Date, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class PublicHoliday(Base):
    __tablename__ = "public_holiday"

    id_holiday: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    date: Mapped[date] = mapped_column(
        Date,
        nullable=False
    )

    is_recurring: Mapped[bool] = mapped_column(
        Boolean,
        default=True
    )

    description: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc)
    )
