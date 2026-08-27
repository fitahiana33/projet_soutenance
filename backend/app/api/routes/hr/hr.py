from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import require_permission, require_active_user, get_db
from app.models.hr.employee import Employee
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
    current_user: UserResponse = Depends(require_permission("HR_READ"))
):
    """Récupère les KPIs globaux des Ressources Humaines."""
    return hr_service.get_hr_overview(db)


# --- EMPLOYES ---

@router.get("/employees", response_model=List[EmployeeResponse])
async def list_employees(
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(require_permission("HR_READ", "EMPLOYEE_READ"))
):
    """Liste des salariés (Filtré par utilisateur pour les simples employés)."""
    return hr_service.get_all_employees(db, actor_user=current_user)


@router.get("/employees/{id_employee}", response_model=EmployeeResponse)
async def get_employee_detail(
    id_employee: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(require_permission("HR_READ", "EMPLOYEE_READ"))
):
    """Fiche complete d'un salarie."""
    employee = hr_service.get_employee_by_id(db, id_employee)
    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employe introuvable.")
    return employee


@router.post("/employees", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
async def create_employee(
    emp_data: EmployeeCreate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(require_permission("HR_CREATE", "HR_MANAGE"))
):
    """Créer une nouvelle fiche salarié."""
    return hr_service.create_employee(db, emp_data.dict())


# --- TEMPS ET ABSENCES ---

@router.get("/time-off", response_model=List[TimeOffRequestResponse])
async def list_time_off_requests(
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(require_permission("HOLIDAY_READ", "HR_READ", "EMPLOYEE_READ"))
):
    """Liste des demandes de congés et d'absences (Filtré par utilisateur)."""
    return hr_service.get_time_off_requests(db, actor_user=current_user)


@router.post("/time-off", response_model=TimeOffRequestResponse, status_code=status.HTTP_201_CREATED)
async def create_time_off_request(
    req_data: TimeOffRequestCreate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(require_active_user)
):
    """Soumettre une demande de congé ou d'absence (Accessible à tout utilisateur actif)."""
    data = req_data.dict()
    data["requested_by_user_id"] = current_user.id_user

    role_names = {r.libelle.upper() for r in getattr(current_user, "roles", [])}
    user_perms = {p.code.upper() for r in getattr(current_user, "roles", []) for p in getattr(r, "permissions", [])}
    has_mgmt = "ADMIN" in role_names or "HR_MANAGE" in user_perms or "HOLIDAY_MANAGE" in user_perms

    if not has_mgmt:
        emp = db.query(Employee).filter(Employee.user_id == current_user.id_user).first()
        if not emp:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Aucun profil employé n'est lié à votre compte."
            )
        data["employee_id"] = emp.id_employee
    else:
        if not data.get("employee_id"):
            emp = db.query(Employee).filter(Employee.user_id == current_user.id_user).first()
            if emp:
                data["employee_id"] = emp.id_employee
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Veuillez indiquer un employee_id valide."
                )

    return hr_service.create_time_off_request(db, data)


@router.put("/time-off/{id_time_off}/validate", response_model=TimeOffRequestResponse)
async def validate_time_off_request(
    id_time_off: int,
    validation: TimeOffValidationRequest,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(require_permission("HOLIDAY_MANAGE", "HR_MANAGE"))
):
    """Validation ou Rejet d'une demande de congé (Opération RH sensible)."""
    try:
        return hr_service.validate_time_off_request(
            db=db,
            id_time_off=id_time_off,
            action=validation.action,
            comment=validation.comment,
            validator_id=current_user.id_user
        )
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# --- GESTION DE LA PAIE ---

@router.get("/payrolls", response_model=List[PayrollResponse])
async def list_payrolls(
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(require_permission("PAYROLL_READ", "HR_READ", "EMPLOYEE_READ"))
):
    """Historique des fiches de paie (Filtré pour chaque employé)."""
    return hr_service.get_payrolls(db, actor_user=current_user)


@router.post("/payrolls", response_model=PayrollResponse, status_code=status.HTTP_201_CREATED)
async def create_payroll(
    pay_data: PayrollCreate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(require_permission("PAYROLL_MANAGE"))
):
    """Générer une nouvelle fiche de paie."""
    return hr_service.create_payroll(db, pay_data.dict())


# --- PERFORMANCE & COMPETENCES ---

@router.get("/performance", response_model=List[PerformanceEvaluationResponse])
async def list_performance_evaluations(
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(require_permission("HR_READ"))
):
    """Liste des évaluations de performance et bilans de compétences."""
    return hr_service.get_performance_evaluations(db)


@router.post("/performance", response_model=PerformanceEvaluationResponse, status_code=status.HTTP_201_CREATED)
async def create_performance_evaluation(
    eval_data: PerformanceEvaluationCreate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(require_permission("HR_CREATE", "HR_MANAGE"))
):
    """Enregistrer une évaluation de performance."""
    return hr_service.create_performance_evaluation(db, eval_data.dict())
