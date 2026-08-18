from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import Integer, String, Float, DateTime, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class JobOffer(Base):
    __tablename__ = "job_offers"

    id_job: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    department: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    location: Mapped[str] = mapped_column(String(100), nullable=False, default="Antananarivo")
    contract_type: Mapped[str] = mapped_column(String(50), nullable=False, default="CDI")
    experience_required_years: Mapped[float] = mapped_column(Float, nullable=False, default=2.0)
    required_skills: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="OUVERT", index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )


class Candidate(Base):
    __tablename__ = "candidates"

    id_candidate: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(150), nullable=False, unique=True, index=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    degree: Mapped[str] = mapped_column(String(150), nullable=False)
    experience_years: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    skills: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    cv_filename: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="EN_EVALUATION", index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )
