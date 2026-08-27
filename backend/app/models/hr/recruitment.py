from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import Integer, String, Float, DateTime, Date, Text, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

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
    job_offer_id: Mapped[Optional[int]] = mapped_column(ForeignKey("job_offers.id_job"), nullable=True, index=True)
    matching_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    final_decision: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    validated_by_user_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    validated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    employee_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="EN_EVALUATION", index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    job_offer: Mapped[Optional[JobOffer]] = relationship("JobOffer")
    evaluations: Mapped[List["CandidateEvaluation"]] = relationship(
        "CandidateEvaluation", back_populates="candidate", cascade="all, delete-orphan"
    )
    interviews: Mapped[List["CandidateInterview"]] = relationship(
        "CandidateInterview", back_populates="candidate", cascade="all, delete-orphan"
    )


class CandidateEvaluation(Base):
    __tablename__ = "candidate_evaluations"

    id_evaluation: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id_candidate"), nullable=False, index=True)
    evaluator_user_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    strengths: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    weaknesses: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    comments: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    candidate: Mapped[Candidate] = relationship("Candidate", back_populates="evaluations")


class CandidateInterview(Base):
    __tablename__ = "candidate_interviews"

    id_interview: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id_candidate"), nullable=False, index=True)
    interviewer_user_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="PLANIFIE")
    feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    candidate: Mapped[Candidate] = relationship("Candidate", back_populates="interviews")
