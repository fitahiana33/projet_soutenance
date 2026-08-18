from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user, require_permission
from app.schemas.users.user import UserResponse
from app.schemas.hr.employee import (
    EmployeeCreate,
    EmployeeResponse,
    TimeOffRequestCreate,
    TimeOffRequestResponse,
    TimeOffValidationRequest,
    PayrollCreate,
    PayrollResponse,
    PerformanceEvaluationCreate,
    PerformanceEvaluationResponse
)
from app.services.hr import hr_service

router = APIRouter(prefix="/hr", tags=["Ressources Humaines"])


@router.get("/overview")
async def get_hr_overview(
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Récupère les KPIs globaux des Ressources Humaines."""
    return hr_service.get_hr_overview(db)


# --- EMPLOYES ---

@router.get("/employees", response_model=List[EmployeeResponse])
async def list_employees(
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Liste des salariés et fiches employés."""
    return hr_service.get_all_employees(db)


@router.post("/employees", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
async def create_employee(
    emp_data: EmployeeCreate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(require_permission("HR_WRITE"))
):
    """Créer une nouvelle fiche salarié."""
    return hr_service.create_employee(db, emp_data.dict())


# --- TEMPS ET ABSENCES ---

@router.get("/time-off", response_model=List[TimeOffRequestResponse])
async def list_time_off_requests(
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Liste des demandes de congés et d'absences."""
    return hr_service.get_time_off_requests(db)


@router.post("/time-off", response_model=List[TimeOffRequestResponse] if False else TimeOffRequestResponse, status_code=status.HTTP_201_CREATED)
async def create_time_off_request(
    req_data: TimeOffRequestCreate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Soumettre une demande de congé ou d'absence."""
    return hr_service.create_time_off_request(db, req_data.dict())


@router.put("/time-off/{id_time_off}/validate", response_model=TimeOffRequestResponse)
async def validate_time_off_request(
    id_time_off: int,
    validation: TimeOffValidationRequest,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(require_permission("HR_WRITE"))
):
    """Validation ou Rejet d'une demande de congé (Opération RH sensible)."""
    try:
        return hr_service.validate_time_off_request(
            db=db,
            id_time_off=id_time_off,
            action=validation.action,
            comment=validation.comment
        )
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# --- GESTION DE LA PAIE ---

@router.get("/payrolls", response_model=List[PayrollResponse])
async def list_payrolls(
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Historique des fiches de paie."""
    return hr_service.get_payrolls(db)


@router.post("/payrolls", response_model=PayrollResponse, status_code=status.HTTP_201_CREATED)
async def create_payroll(
    pay_data: PayrollCreate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(require_permission("HR_WRITE"))
):
    """Générer une nouvelle fiche de paie."""
    return hr_service.create_payroll(db, pay_data.dict())


# --- PERFORMANCE & COMPETENCES ---

@router.get("/performance", response_model=List[PerformanceEvaluationResponse])
async def list_performance_evaluations(
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Liste des évaluations de performance et bilans de compétences."""
    return hr_service.get_performance_evaluations(db)


@router.post("/performance", response_model=PerformanceEvaluationResponse, status_code=status.HTTP_201_CREATED)
async def create_performance_evaluation(
    eval_data: PerformanceEvaluationCreate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(require_permission("HR_WRITE"))
):
    """Enregistrer une évaluation de performance."""
    return hr_service.create_performance_evaluation(db, eval_data.dict())
