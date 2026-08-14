from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status

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
    current_user: UserResponse = Depends(get_current_user)
):
    """Récupère les KPIs globaux des Ressources Humaines."""
    return await hr_service.get_hr_overview()


# --- EMPLOYES ---

@router.get("/employees", response_model=List[EmployeeResponse])
async def list_employees(
    current_user: UserResponse = Depends(get_current_user)
):
    """Liste des salariés et fiches employés."""
    return await hr_service.get_all_employees()


@router.post("/employees", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
async def create_employee(
    emp_data: EmployeeCreate,
    current_user: UserResponse = Depends(require_permission("HR_WRITE"))
):
    """Créer une nouvelle fiche salarié."""
    return await hr_service.create_employee(emp_data.dict())


# --- TEMPS ET ABSENCES ---

@router.get("/time-off", response_model=List[TimeOffRequestResponse])
async def list_time_off_requests(
    current_user: UserResponse = Depends(get_current_user)
):
    """Liste des demandes de congés et d'absences."""
    return await hr_service.get_time_off_requests()


@router.post("/time-off", response_model=TimeOffRequestResponse, status_code=status.HTTP_201_CREATED)
async def create_time_off_request(
    req_data: TimeOffRequestCreate,
    current_user: UserResponse = Depends(get_current_user)
):
    """Soumettre une demande de congé ou d'absence."""
    return await hr_service.create_time_off_request(req_data.dict())


@router.put("/time-off/{id_time_off}/validate", response_model=TimeOffRequestResponse)
async def validate_time_off_request(
    id_time_off: int,
    validation: TimeOffValidationRequest,
    current_user: UserResponse = Depends(require_permission("HR_WRITE"))
):
    """Validation ou Rejet d'une demande de congé (Opération RH sensible)."""
    try:
        return await hr_service.validate_time_off_request(
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
    current_user: UserResponse = Depends(get_current_user)
):
    """Historique des fiches de paie."""
    return await hr_service.get_payrolls()


@router.post("/payrolls", response_model=PayrollResponse, status_code=status.HTTP_201_CREATED)
async def create_payroll(
    pay_data: PayrollCreate,
    current_user: UserResponse = Depends(require_permission("HR_WRITE"))
):
    """Générer une nouvelle fiche de paie."""
    return await hr_service.create_payroll(pay_data.dict())


# --- PERFORMANCE & COMPETENCES ---

@router.get("/performance", response_model=List[PerformanceEvaluationResponse])
async def list_performance_evaluations(
    current_user: UserResponse = Depends(get_current_user)
):
    """Liste des évaluations de performance et bilans de compétences."""
    return await hr_service.get_performance_evaluations()


@router.post("/performance", response_model=PerformanceEvaluationResponse, status_code=status.HTTP_201_CREATED)
async def create_performance_evaluation(
    eval_data: PerformanceEvaluationCreate,
    current_user: UserResponse = Depends(require_permission("HR_WRITE"))
):
    """Enregistrer une évaluation de performance."""
    return await hr_service.create_performance_evaluation(eval_data.dict())
