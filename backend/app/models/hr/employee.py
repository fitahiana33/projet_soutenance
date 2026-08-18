from datetime import datetime, timezone, date
from typing import Optional, List
from sqlalchemy import (
    Integer, String, Float, Boolean, DateTime, Date, ForeignKey, Text, JSON
)
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.core.database import Base


class Employee(Base):
    __tablename__ = "employees"

    id_employee: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    matricule: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    user_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("user_.id_user"), nullable=True
    )
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    email: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    gender: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    birth_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    place_of_birth: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    nationality: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    cin_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    cin_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    department: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    job_title: Mapped[str] = mapped_column(String(150), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False, default="Employé")
    contract_type: Mapped[str] = mapped_column(String(30), nullable=False, default="CDI")
    hire_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    probation_end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    contract_end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    base_salary: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    currency: Mapped[str] = mapped_column(String(10), nullable=False, default="Ar")
    manager_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    bank_name: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    bank_account: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    children_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    marital_status: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="ACTIF", index=True)
    departure_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    departure_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    photo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    emergency_contact_name: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    emergency_contact_phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    skills_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    diplomas_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    experiences_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    user: Mapped[Optional["User"]] = relationship("User")
    time_off_requests: Mapped[List["TimeOffRequest"]] = relationship(
        "TimeOffRequest", back_populates="employee"
    )


class TimeOffRequest(Base):
    __tablename__ = "time_off_requests"

    id_time_off: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    employee_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("employees.id_employee"), nullable=False
    )
    employee_name: Mapped[str] = mapped_column(String(200), nullable=False)
    department: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    leave_type: Mapped[str] = mapped_column(
        String(30), nullable=False, default="PAYE", index=True
    )
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    days_count: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    half_day: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    document_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="EN_ATTENTE", index=True)
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    requested_by_user_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    validated_by_user_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    requested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    validated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    employee: Mapped[Employee] = relationship("Employee", back_populates="time_off_requests")


class PayrollEntry(Base):
    __tablename__ = "payroll_entries"

    id_payroll: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    employee_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("employees.id_employee"), nullable=False
    )
    employee_name: Mapped[str] = mapped_column(String(200), nullable=False)
    department: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    job_title: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    period: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    payroll_date: Mapped[date] = mapped_column(Date, default=lambda: datetime.now(timezone.utc).date())

    base_salary: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    bonus: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    bonus_seniority: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    bonus_performance: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    bonus_misc: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    deduction_absences: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    overtime_hours: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    overtime_30_hours: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    overtime_40_hours: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    overtime_50_hours: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    overtime_100_hours: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    night_hours: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    overtime_amount: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    gross_salary: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    cnaps_employee: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    ostie_employee: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    total_social_contributions: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    irsa: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    children_deduction: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    children_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    advances: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    other_deductions: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    deductions: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    net_salary: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    cnaps_employer: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    ostie_employer: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    employer_charges: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    total_cost: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    payment_status: Mapped[str] = mapped_column(String(30), nullable=False, default="CALCULE", index=True)
    payment_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    payment_method: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_by_user_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    employee: Mapped[Employee] = relationship("Employee")


class PerformanceEvaluation(Base):
    __tablename__ = "performance_evaluations"

    id_evaluation: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    employee_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("employees.id_employee"), nullable=False
    )
    employee_name: Mapped[str] = mapped_column(String(200), nullable=False)
    department: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    evaluation_period: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    evaluation_date: Mapped[date] = mapped_column(Date, default=lambda: datetime.now(timezone.utc).date())

    performance_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    rating_label: Mapped[str] = mapped_column(String(30), nullable=False, default="SATISFAISANT")

    goals_achieved: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    strengths: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    areas_to_improve: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    skills: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    training_recommended: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    career_evolution_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    evaluated_by_user_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    employee_signature: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    manager_signature: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    evaluated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    employee: Mapped[Employee] = relationship("Employee")
