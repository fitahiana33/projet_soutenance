from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class EmployeeBase(BaseModel):
    matricule: Optional[str] = Field(None, description="Matricule employé (ex: EMP-2026-001)")
    first_name: str = Field(..., description="Prénom")
    last_name: str = Field(..., description="Nom")
    email: str = Field(..., description="Email professionnel")
    phone: Optional[str] = Field(None, description="Téléphone")
    department: str = Field(..., description="Service / Département (ex: IT, Ventes, Finance)")
    job_title: str = Field(..., description="Poste occupé")
    contract_type: str = Field("CDI", description="Type de contrat (CDI, CDD, Stage, Prestation)")
    hire_date: str = Field(..., description="Date d'embauche (YYYY-MM-DD)")
    base_salary: float = Field(..., ge=0.0, description="Salaire de base mensuel brut (€)")
    status: str = Field("ACTIF", description="Statut (ACTIF, CONGE, SUSPENDU, PARTI)")


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeResponse(EmployeeBase):
    id_employee: int
    seniority_months: int
    seniority_label: str
    created_at: str


class TimeOffRequestCreate(BaseModel):
    employee_id: int
    leave_type: str = Field("PAYE", description="PAYE, MALADIE, RTT, SANS_SOLDE")
    start_date: str
    end_date: str
    days_count: float = Field(..., gt=0.0)
    reason: Optional[str] = None


class TimeOffRequestResponse(BaseModel):
    id_time_off: int
    employee_id: int
    employee_name: str
    department: str
    leave_type: str
    start_date: str
    end_date: str
    days_count: float
    reason: Optional[str] = None
    status: str  # EN_ATTENTE, ACCEPTE, REFUSE
    requested_at: str


class TimeOffValidationRequest(BaseModel):
    action: str = Field(..., description="ACCEPTER ou REFUSER")
    comment: Optional[str] = None


class PayrollCreate(BaseModel):
    employee_id: int
    period: str = Field(..., description="Période de paie (ex: 2026-08)")
    gross_salary: float = Field(..., ge=0.0)
    bonus: float = Field(0.0, ge=0.0)
    overtime_hours: float = Field(0.0, ge=0.0)
    overtime_amount: float = Field(0.0, ge=0.0)
    deductions: float = Field(0.0, ge=0.0)
    employer_charges: float = Field(0.0, ge=0.0)


class PayrollResponse(BaseModel):
    id_payroll: int
    employee_id: int
    employee_name: str
    department: str
    job_title: str
    period: str
    gross_salary: float
    bonus: float
    overtime_hours: float
    overtime_amount: float
    deductions: float
    net_salary: float
    employer_charges: float
    payment_status: str  # ECHU, PAYE, EN_TRAITEMENT
    created_at: str


class PerformanceEvaluationCreate(BaseModel):
    employee_id: int
    evaluation_period: str = Field(..., description="ex: Année 2026 / Q3 2026")
    performance_score: float = Field(..., ge=0.0, le=100.0)
    goals_achieved: str
    skills: List[str] = Field(default_factory=list)
    training_recommended: Optional[str] = None
    career_evolution_notes: Optional[str] = None


class PerformanceEvaluationResponse(BaseModel):
    id_evaluation: int
    employee_id: int
    employee_name: str
    department: str
    evaluation_period: str
    performance_score: float
    goals_achieved: str
    skills: List[str]
    training_recommended: Optional[str] = None
    career_evolution_notes: Optional[str] = None
    rating_label: str  # EXCELLENT, SATISFAISANT, A_AMELIORER
    evaluated_at: str
