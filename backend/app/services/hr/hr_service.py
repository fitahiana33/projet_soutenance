import logging
import json
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone, date
from sqlalchemy.orm import Session

from app.models.hr.employee import (
    Employee,
    TimeOffRequest,
    PayrollEntry,
    PerformanceEvaluation
)
from app.services.audit.audit_service import log_action
from app.services.system.system_service import get_business_parameters

logger = logging.getLogger(__name__)

PAYROLL_CONFIG = {
    "social_security_rate": 0.01,
    "health_insurance_rate": 0.01,
    "employer_social_security_rate": 0.13,
    "employer_health_rate": 0.05,
    "overtime_multiplier": 1.5,
    "annual_leave_days": 30,
}


# ==============================================================================
# HELPERS: Conversion SQLAlchemy -> Dict (retro-compatible routes)
# ==============================================================================

def _date_iso(d: Optional[date]) -> Optional[str]:
    return d.isoformat() if d else None


def _dt_iso(dt: Optional[datetime]) -> Optional[str]:
    return dt.isoformat() if dt else None


def _employee_to_dict(emp: Employee) -> Dict[str, Any]:
    months, label = _calculate_seniority(emp.hire_date)
    return {
        "id_employee": emp.id_employee,
        "matricule": emp.matricule,
        "user_id": emp.user_id,
        "first_name": emp.first_name,
        "last_name": emp.last_name,
        "email": emp.email,
        "phone": emp.phone,
        "address": emp.address,
        "gender": emp.gender,
        "date_of_naissance": _date_iso(emp.birth_date),
        "cin": emp.cin_number,
        "civil_status": emp.marital_status,
        "marital_status": emp.marital_status,
        "number_of_children": emp.children_count,
        "position": emp.job_title,
        "department": emp.department,
        "status": emp.status,
        "hiring_date": _date_iso(emp.hire_date),
        "hire_date": _date_iso(emp.hire_date) or "2026-01-01",
        "end_contract_date": _date_iso(emp.contract_end_date),
        "base_salary": emp.base_salary,
        "currency": emp.currency,
        "bank_name": emp.bank_name,
        "bank_account": emp.bank_account,
        "rib": emp.bank_account,
        "emergency_contact_name": emp.emergency_contact_name,
        "emergency_contact_phone": emp.emergency_contact_phone,
        "emergency_contact_relation": None,
        "supervisor_id": emp.manager_id,
        "job_title": emp.job_title,
        "category": emp.category,
        "contract_type": emp.contract_type,
        "children_count": emp.children_count,
        "manager_id": emp.manager_id,
        "photo_url": emp.photo_url,
        "notes": emp.notes,
        "created_at": _dt_iso(emp.created_at),
        "updated_at": _dt_iso(emp.updated_at),
        "seniority_months": months,
        "seniority_label": label,
    }


def _timeoff_to_dict(t: TimeOffRequest) -> Dict[str, Any]:
    return {
        "id_request": t.id_time_off,
        "id_time_off": t.id_time_off,
        "employee_id": t.employee_id,
        "employee_name": t.employee_name,
        "department": t.department,
        "leave_type": t.leave_type,
        "start_date": _date_iso(t.start_date),
        "end_date": _date_iso(t.end_date),
        "number_of_days": t.days_count,
        "days_count": t.days_count,
        "reason": t.reason,
        "supporting_document": t.document_url,
        "document_url": t.document_url,
        "status": t.status,
        "approved_by": t.validated_by_user_id,
        "approved_at": _dt_iso(t.validated_at),
        "approver_notes": t.comment,
        "comment": t.comment,
        "half_day": t.half_day,
        "requested_by_user_id": t.requested_by_user_id,
        "validated_by_user_id": t.validated_by_user_id,
        "requested_at": _dt_iso(t.requested_at),
        "validated_at": _dt_iso(t.validated_at),
        "created_at": _dt_iso(t.created_at),
        "updated_at": _dt_iso(t.created_at),
    }


def _payroll_to_dict(p: PayrollEntry) -> Dict[str, Any]:
    bonuses_json = json.dumps({
        "bonus": p.bonus,
        "bonus_seniority": p.bonus_seniority,
        "bonus_performance": p.bonus_performance,
        "bonus_misc": p.bonus_misc,
    })
    allowances_json = json.dumps({
        "deduction_absences": p.deduction_absences,
        "advances": p.advances,
        "other_deductions": p.other_deductions,
    })
    return {
        "id_payroll": p.id_payroll,
        "employee_id": p.employee_id,
        "employee_name": p.employee_name,
        "matricule": None,
        "period_month": None,
        "period_year": None,
        "period": p.period,
        "base_salary": p.base_salary,
        "position": p.job_title,
        "department": p.department,
        "number_of_children": p.children_count,
        "overtime_hours_30": p.overtime_30_hours,
        "overtime_hours_40": p.overtime_40_hours,
        "overtime_hours_50": p.overtime_50_hours,
        "overtime_hours_100": p.overtime_100_hours,
        "overtime_hours_night": p.night_hours,
        "overtime_premium_total": p.overtime_amount,
        "bonuses_json": bonuses_json,
        "allowances_json": allowances_json,
        "gross_salary": p.gross_salary,
        "cnaps_employee": p.cnaps_employee,
        "cnaps_employer": p.cnaps_employer,
        "ostie_employee": p.ostie_employee,
        "ostie_employer": p.ostie_employer,
        "irsa": p.irsa,
        "total_deductions": p.deductions,
        "net_salary": p.net_salary,
        "payment_date": _date_iso(p.payment_date),
        "payment_method": p.payment_method,
        "payslip_pdf_url": None,
        "status": p.payment_status,
        "validated_by": None,
        "validated_at": None,
        "created_at": _dt_iso(p.created_at),
        "created_by_user_id": p.created_by_user_id,
        "notes": p.notes,
        "job_title": p.job_title,
        "category": p.category,
        "payroll_date": _date_iso(p.payroll_date),
        "bonus": p.bonus,
        "bonus_seniority": p.bonus_seniority,
        "bonus_performance": p.bonus_performance,
        "bonus_misc": p.bonus_misc,
        "deduction_absences": p.deduction_absences,
        "overtime_hours": p.overtime_hours,
        "overtime_30_hours": p.overtime_30_hours,
        "overtime_40_hours": p.overtime_40_hours,
        "overtime_50_hours": p.overtime_50_hours,
        "overtime_100_hours": p.overtime_100_hours,
        "night_hours": p.night_hours,
        "overtime_amount": p.overtime_amount,
        "total_social_contributions": p.total_social_contributions,
        "children_deduction": p.children_deduction,
        "children_count": p.children_count,
        "advances": p.advances,
        "other_deductions": p.other_deductions,
        "deductions": p.deductions,
        "employer_charges": p.employer_charges,
        "total_cost": p.total_cost,
        "payment_status": p.payment_status,
        "updated_at": _dt_iso(p.updated_at),
    }


def _evaluation_to_dict(e: PerformanceEvaluation) -> Dict[str, Any]:
    skills_list = []
    if e.skills:
        try:
            skills_list = json.loads(e.skills) if isinstance(e.skills, str) else e.skills
        except Exception:
            skills_list = [str(e.skills)]
    return {
        "id_evaluation": e.id_evaluation,
        "employee_id": e.employee_id,
        "employee_name": e.employee_name,
        "evaluation_period": e.evaluation_period,
        "evaluation_date": _date_iso(e.evaluation_date),
        "evaluator_id": e.evaluated_by_user_id,
        "evaluator_name": None,
        "overall_score": e.performance_score,
        "skills_json": e.skills,
        "goals_json": e.goals_achieved,
        "achievements": e.goals_achieved,
        "areas_improvement": e.areas_to_improve,
        "training_recommendations": e.training_recommended,
        "employee_signature": e.employee_signature,
        "evaluator_signature": e.manager_signature,
        "employee_signed_at": None,
        "evaluator_signed_at": None,
        "notes": e.career_evolution_notes,
        "created_at": _dt_iso(e.created_at),
        "department": e.department,
        "performance_score": e.performance_score,
        "rating_label": e.rating_label,
        "goals_achieved": e.goals_achieved or "",
        "strengths": e.strengths,
        "areas_to_improve": e.areas_to_improve,
        "skills": skills_list,
        "training_recommended": e.training_recommended,
        "career_evolution_notes": e.career_evolution_notes,
        "evaluated_by_user_id": e.evaluated_by_user_id,
        "manager_signature": e.manager_signature,
        "evaluated_at": _dt_iso(e.evaluated_at),
    }


# ==============================================================================
# HELPERS: Calculs métier
# ==============================================================================

def _calculate_seniority(hire_date_value) -> tuple[int, str]:
    try:
        if isinstance(hire_date_value, str):
            hire_dt = datetime.strptime(hire_date_value, "%Y-%m-%d")
        elif isinstance(hire_date_value, date):
            hire_dt = datetime.combine(hire_date_value, datetime.min.time())
        else:
            return 0, "Moins d'un mois"

        now = datetime.now()
        months = (now.year - hire_dt.year) * 12 + (now.month - hire_dt.month)
        months = max(0, months)

        years = months // 12
        rem_months = months % 12

        if years > 0 and rem_months > 0:
            label = f"{years} an{'s' if years > 1 else ''} et {rem_months} mois"
        elif years > 0:
            label = f"{years} an{'s' if years > 1 else ''}"
        else:
            label = f"{months} mois"

        return months, label
    except Exception:
        return 0, "Moins d'un mois"


def calculate_irsa_madagascar(taxable_base: float, children_count: int = 0) -> float:
    """
    Calcul IRSA Madagascar - barème progressif IMPÉRATIF:
    - 0% ≤ 350 000 Ar
    - 5% 350 001 - 400 000 Ar
    - 10% 400 001 - 500 000 Ar
    - 15% 500 001 - 600 000 Ar
    - 20% 600 001 - 800 000 Ar
    - 25% > 800 000 Ar
    Déduction: 2 000 Ar / enfant
    IRSA minimum: 3 000 Ar
    """
    if taxable_base <= 0:
        return 0.0

    irsa_brut = 0.0

    tranches = [
        (0, 350000, 0.00),
        (350001, 400000, 0.05),
        (400001, 500000, 0.10),
        (500001, 600000, 0.15),
        (600001, 800000, 0.20),
        (800001, float('inf'), 0.25),
    ]

    for min_t, max_t, rate in tranches:
        if taxable_base <= min_t:
            continue
        upper = min(taxable_base, max_t)
        base_tranche = upper - min_t + 1 if min_t > 0 else upper - min_t
        if min_t == 0:
            base_tranche = upper
        irsa_brut += base_tranche * rate

    deduction_enfants = max(0, children_count) * 2000.0
    irsa_net = irsa_brut - deduction_enfants
    irsa_net = max(0.0, irsa_net)

    if irsa_net > 0 and irsa_net < 3000:
        irsa_net = 3000.0

    return round(irsa_net, 2)


def calculate_payroll(
    base_salary: float,
    children_count: int = 0,
    bonuses: Optional[Dict[str, float]] = None,
    overtime: Optional[Dict[str, float]] = None,
    other_allowances: Optional[Dict[str, float]] = None,
    deductions_absences: float = 0.0,
) -> Dict[str, Any]:
    """
    Calcul PAIE MADAGASCAR IMPÉRATIF selon barèmes légaux:
    - CNAPS Salarial: 1% * min(base_salary, 568 000)
    - CNAPS Patronal: 13% * min(base_salary, 568 000)
    - OSTIE Salarial: 1% * brut
    - OSTIE Patronal: 5% * brut
    - IRSA: barème progressif tranches + 2000/enfant, min 3000 Ar
    - Net = (base + primes + HS) - (CNAPS_sal + OSTIE_sal + IRSA)
    """
    bonuses = bonuses or {}
    overtime = overtime or {}
    other_allowances = other_allowances or {}

    sys_params = get_business_parameters()
    rate_ot30 = sys_params.get("overtime_30_rate", 1.30)
    rate_ot40 = sys_params.get("overtime_40_rate", 1.40)
    rate_ot50 = sys_params.get("overtime_50_rate", 1.50)
    rate_ot100 = sys_params.get("overtime_100_rate", 2.00)
    rate_night = sys_params.get("overtime_night_rate", 1.50)

    hourly_rate = base_salary / 173.33 if base_salary > 0 else 0

    ot_30 = float(overtime.get("overtime_hours_30", 0.0) or overtime.get("overtime_30_hours", 0.0))
    ot_40 = float(overtime.get("overtime_hours_40", 0.0) or overtime.get("overtime_40_hours", 0.0))
    ot_50 = float(overtime.get("overtime_hours_50", 0.0) or overtime.get("overtime_50_hours", 0.0))
    ot_100 = float(overtime.get("overtime_hours_100", 0.0) or overtime.get("overtime_100_hours", 0.0))
    ot_night = float(overtime.get("overtime_hours_night", 0.0) or overtime.get("night_hours", 0.0))
    ot_total_hrs = float(overtime.get("overtime_hours", 0.0)) or (ot_30 + ot_40 + ot_50 + ot_100)

    ot_amount = round(
        (ot_30 * hourly_rate * rate_ot30) +
        (ot_40 * hourly_rate * rate_ot40) +
        (ot_50 * hourly_rate * rate_ot50) +
        (ot_100 * hourly_rate * rate_ot100) +
        (ot_night * hourly_rate * rate_night),
        2
    )
    if ot_amount == 0 and ot_total_hrs > 0:
        ot_amount = round(ot_total_hrs * hourly_rate * rate_ot50, 2)

    bonus_misc = float(bonuses.get("bonus_misc", 0.0) or bonuses.get("bonus", 0.0))
    bonus_seniority = float(bonuses.get("bonus_seniority", 0.0))
    bonus_performance = float(bonuses.get("bonus_performance", 0.0))
    total_bonus = bonus_misc + bonus_seniority + bonus_performance

    base_after_absences = max(0.0, base_salary - deductions_absences)
    gross_salary = round(base_after_absences + total_bonus + ot_amount, 2)

    cnaps_plafond = 568000.0
    cnaps_base = min(base_salary, cnaps_plafond)

    cnaps_employee = round(cnaps_base * 0.01, 2)
    cnaps_employer = round(cnaps_base * 0.13, 2)
    ostie_employee = round(gross_salary * 0.01, 2)
    ostie_employer = round(gross_salary * 0.05, 2)

    cotisations_salariales = round(cnaps_employee + ostie_employee, 2)

    base_imposable = max(0.0, gross_salary - cotisations_salariales)

    irsa = calculate_irsa_madagascar(base_imposable, children_count)

    children_deduction = max(0, children_count) * 2000.0

    advances = float(other_allowances.get("advances", 0.0))
    other_deductions = float(other_allowances.get("other_deductions", 0.0) or other_allowances.get("deductions", 0.0))

    total_deductions = round(cotisations_salariales + irsa + advances + other_deductions, 2)
    net_salary = max(0.0, round(gross_salary - total_deductions, 2))

    employer_charges = round(cnaps_employer + ostie_employer, 2)
    total_cost = round(gross_salary + employer_charges, 2)

    return {
        "base_salary": base_salary,
        "gross_salary": gross_salary,
        "base_after_absences": base_after_absences,
        "bonus_misc": bonus_misc,
        "bonus_seniority": bonus_seniority,
        "bonus_performance": bonus_performance,
        "total_bonus": total_bonus,
        "overtime_30_hours": ot_30,
        "overtime_40_hours": ot_40,
        "overtime_50_hours": ot_50,
        "overtime_100_hours": ot_100,
        "night_hours": ot_night,
        "overtime_hours": ot_total_hrs,
        "overtime_amount": ot_amount,
        "cnaps_employee": cnaps_employee,
        "cnaps_employer": cnaps_employer,
        "ostie_employee": ostie_employee,
        "ostie_employer": ostie_employer,
        "total_social_contributions": cotisations_salariales,
        "base_imposable": base_imposable,
        "irsa": irsa,
        "children_deduction": children_deduction,
        "children_count": children_count,
        "advances": advances,
        "other_deductions": other_deductions,
        "deductions": total_deductions,
        "total_deductions": total_deductions,
        "net_salary": net_salary,
        "employer_charges": employer_charges,
        "total_cost": total_cost,
        "deduction_absences": deductions_absences,
    }


# ==============================================================================
# EMPLOYES
# ==============================================================================

def get_all_employees(db: Session) -> List[Dict[str, Any]]:
    employees = db.query(Employee).order_by(Employee.last_name.asc()).all()
    return [_employee_to_dict(e) for e in employees]


def get_employee_by_id(db: Session, id_employee: int) -> Optional[Dict[str, Any]]:
    emp = db.query(Employee).filter(Employee.id_employee == id_employee).first()
    return _employee_to_dict(emp) if emp else None


def create_employee(db: Session, emp_data: Dict[str, Any]) -> Dict[str, Any]:
    existing_count = db.query(Employee).count()
    new_id = existing_count + 1
    mat = emp_data.get("matricule") or f"EMP-2026-{new_id:03d}"

    def _d(key):
        return emp_data.get(key, emp_data.get(
            key.replace("date_of_naissance", "birth_date")
               .replace("hiring_date", "hire_date")
               .replace("end_contract_date", "contract_end_date")
               .replace("number_of_children", "children_count")
               .replace("position", "job_title")
               .replace("cin", "cin_number")
               .replace("supervisor_id", "manager_id")
        ))

    def _parse_date(val):
        if val is None:
            return None
        if isinstance(val, date):
            return val
        if isinstance(val, str):
            try:
                return datetime.strptime(val, "%Y-%m-%d").date()
            except Exception:
                return None
        return None

    children_val = _d("number_of_children") or _d("children_count") or 0

    emp = Employee(
        matricule=mat,
        user_id=_d("user_id"),
        first_name=emp_data["first_name"],
        last_name=emp_data["last_name"],
        email=_d("email"),
        phone=_d("phone"),
        address=_d("address"),
        gender=_d("gender"),
        birth_date=_parse_date(_d("date_of_naissance") or _d("birth_date")),
        cin_number=_d("cin") or _d("cin_number"),
        department=emp_data.get("department") or emp_data.get("job_department") or "Général",
        job_title=emp_data.get("position") or emp_data.get("job_title") or "Employé",
        category=emp_data.get("category", "Employé"),
        contract_type=emp_data.get("contract_type", "CDI"),
        hire_date=_parse_date(_d("hiring_date") or _d("hire_date")) or date.today(),
        contract_end_date=_parse_date(_d("end_contract_date") or _d("contract_end_date")),
        base_salary=float(emp_data.get("base_salary", 0.0)),
        currency=emp_data.get("currency", "Ar"),
        manager_id=_d("supervisor_id") or _d("manager_id"),
        bank_name=_d("bank_name"),
        bank_account=_d("bank_account") or _d("rib"),
        children_count=int(children_val) if children_val is not None else 0,
        marital_status=_d("marital_status") or _d("civil_status"),
        status=emp_data.get("status", "ACTIF"),
        emergency_contact_name=_d("emergency_contact_name"),
        emergency_contact_phone=_d("emergency_contact_phone"),
        notes=_d("notes"),
    )
    db.add(emp)
    db.commit()
    db.refresh(emp)

    log_action(
        db,
        action="CREATE",
        module="RH",
        target_entity=f"EMPLOYEE:{emp.id_employee}",
        details=f"Création employé: {emp.first_name} {emp.last_name} ({mat})",
        new_values=_employee_to_dict(emp),
    )

    return _employee_to_dict(emp)


def update_employee(db: Session, id_employee: int, emp_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    emp = db.query(Employee).filter(Employee.id_employee == id_employee).first()
    if not emp:
        return None

    old_values = _employee_to_dict(emp)

    field_mapping = {
        "matricule": "matricule",
        "user_id": "user_id",
        "first_name": "first_name",
        "last_name": "last_name",
        "email": "email",
        "phone": "phone",
        "address": "address",
        "gender": "gender",
        "date_of_naissance": "birth_date",
        "birth_date": "birth_date",
        "cin": "cin_number",
        "cin_number": "cin_number",
        "department": "department",
        "position": "job_title",
        "job_title": "job_title",
        "category": "category",
        "contract_type": "contract_type",
        "hiring_date": "hire_date",
        "hire_date": "hire_date",
        "end_contract_date": "contract_end_date",
        "contract_end_date": "contract_end_date",
        "base_salary": "base_salary",
        "currency": "currency",
        "supervisor_id": "manager_id",
        "manager_id": "manager_id",
        "bank_name": "bank_name",
        "bank_account": "bank_account",
        "rib": "bank_account",
        "number_of_children": "children_count",
        "children_count": "children_count",
        "marital_status": "marital_status",
        "civil_status": "marital_status",
        "status": "status",
        "emergency_contact_name": "emergency_contact_name",
        "emergency_contact_phone": "emergency_contact_phone",
        "notes": "notes",
    }

    date_fields = {"birth_date", "hire_date", "contract_end_date"}

    for src_key, dst_key in field_mapping.items():
        if src_key in emp_data and emp_data[src_key] is not None:
            val = emp_data[src_key]
            if dst_key in date_fields:
                if isinstance(val, str):
                    try:
                        val = datetime.strptime(val, "%Y-%m-%d").date()
                    except Exception:
                        continue
                elif isinstance(val, date):
                    pass
                else:
                    continue
            if dst_key == "base_salary":
                val = float(val)
            if dst_key == "children_count":
                val = int(val)
            setattr(emp, dst_key, val)

    db.commit()
    db.refresh(emp)

    log_action(
        db,
        action="UPDATE",
        module="RH",
        target_entity=f"EMPLOYEE:{id_employee}",
        details=f"Mise à jour fiche employé #{id_employee}",
        old_values=old_values,
        new_values=_employee_to_dict(emp),
    )

    return _employee_to_dict(emp)


def delete_employee(db: Session, id_employee: int) -> bool:
    emp = db.query(Employee).filter(Employee.id_employee == id_employee).first()
    if not emp:
        return False

    old_values = _employee_to_dict(emp)
    db.delete(emp)
    db.commit()

    log_action(
        db,
        action="DELETE",
        module="RH",
        target_entity=f"EMPLOYEE:{id_employee}",
        details=f"Suppression employé: {emp.first_name} {emp.last_name}",
        old_values=old_values,
    )
    return True


# ==============================================================================
# TEMPS ET ABSENCES
# ==============================================================================

def get_time_off_requests(db: Session) -> List[Dict[str, Any]]:
    items = db.query(TimeOffRequest).order_by(TimeOffRequest.created_at.desc()).all()
    return [_timeoff_to_dict(t) for t in items]


def create_time_off_request(db: Session, req_data: Dict[str, Any]) -> Dict[str, Any]:
    emp = db.query(Employee).filter(Employee.id_employee == req_data["employee_id"]).first()
    emp_name = f"{emp.first_name} {emp.last_name}" if emp else f"Employé #{req_data['employee_id']}"
    dept = emp.department if emp else "Général"

    def _parse_date(val):
        if val is None:
            return None
        if isinstance(val, date):
            return val
        if isinstance(val, str):
            try:
                return datetime.strptime(val, "%Y-%m-%d").date()
            except Exception:
                return None
        return None

    days = float(req_data.get("number_of_days") or req_data.get("days_count") or 0.0)

    t = TimeOffRequest(
        employee_id=req_data["employee_id"],
        employee_name=emp_name,
        department=dept,
        leave_type=req_data.get("leave_type", "PAYE"),
        start_date=_parse_date(req_data["start_date"]) or date.today(),
        end_date=_parse_date(req_data["end_date"]) or date.today(),
        days_count=days,
        half_day=bool(req_data.get("half_day", False)),
        reason=req_data.get("reason"),
        document_url=req_data.get("supporting_document") or req_data.get("document_url"),
        status="EN_ATTENTE",
        comment=None,
        requested_by_user_id=req_data.get("requested_by_user_id"),
    )
    db.add(t)
    db.commit()
    db.refresh(t)

    log_action(
        db,
        action="CREATE",
        module="RH",
        target_entity=f"TIME_OFF:{t.id_time_off}",
        details=f"Demande congé: {emp_name} ({t.leave_type}, {days}j)",
        new_values=_timeoff_to_dict(t),
    )

    return _timeoff_to_dict(t)


def validate_time_off_request(
    db: Session,
    id_time_off: int,
    action: str,
    comment: Optional[str] = None,
    validator_id: Optional[int] = None,
) -> Dict[str, Any]:
    to = db.query(TimeOffRequest).filter(TimeOffRequest.id_time_off == id_time_off).first()
    if not to:
        raise RuntimeError(f"Demande de congé #{id_time_off} non trouvée.")

    old_values = _timeoff_to_dict(to)
    action_up = action.upper()

    if action_up in ["ACCEPTER", "VALIDER", "APPROUVER"]:
        to.status = "ACCEPTE"
    elif action_up in ["REFUSER", "REJETER"]:
        to.status = "REFUSE"
        if comment:
            to.comment = comment
    elif action_up in ["ANNULER"]:
        to.status = "ANNULE"
    else:
        raise ValueError("Action invalide.")

    if to.status != "EN_ATTENTE":
        to.validated_by_user_id = validator_id
        to.validated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(to)

    log_action(
        db,
        action="VALIDATE",
        module="RH",
        target_entity=f"TIME_OFF:{id_time_off}",
        details=f"Validation congé #{id_time_off}: {action} -> {to.status}",
        old_values=old_values,
        new_values=_timeoff_to_dict(to),
    )

    return _timeoff_to_dict(to)


# ==============================================================================
# GESTION DE LA PAIE
# ==============================================================================

def get_payrolls(db: Session) -> List[Dict[str, Any]]:
    items = db.query(PayrollEntry).order_by(PayrollEntry.created_at.desc()).all()
    return [_payroll_to_dict(p) for p in items]


def create_payroll(db: Session, pay_data: Dict[str, Any]) -> Dict[str, Any]:
    emp = db.query(Employee).filter(Employee.id_employee == pay_data["employee_id"]).first()
    emp_name = f"{emp.first_name} {emp.last_name}" if emp else f"Employé #{pay_data['employee_id']}"
    dept = emp.department if emp else "Général"
    job = emp.job_title if emp else "Poste"
    cat = emp.category if emp else "Employé"
    children_count = int(pay_data.get("number_of_children") or pay_data.get("children_count") or (emp.children_count if emp else 0))
    base_salary = float(pay_data.get("base_salary") or pay_data.get("gross_salary") or (emp.base_salary if emp else 0.0))

    calc = calculate_payroll(
        base_salary=base_salary,
        children_count=children_count,
        bonuses={
            "bonus_misc": float(pay_data.get("bonus_misc", 0.0) or pay_data.get("bonus", 0.0)),
            "bonus_seniority": float(pay_data.get("bonus_seniority", 0.0)),
            "bonus_performance": float(pay_data.get("bonus_performance", 0.0)),
        },
        overtime={
            "overtime_30_hours": float(pay_data.get("overtime_hours_30", 0.0) or pay_data.get("overtime_30_hours", 0.0)),
            "overtime_40_hours": float(pay_data.get("overtime_hours_40", 0.0) or pay_data.get("overtime_40_hours", 0.0)),
            "overtime_50_hours": float(pay_data.get("overtime_hours_50", 0.0) or pay_data.get("overtime_50_hours", 0.0)),
            "overtime_100_hours": float(pay_data.get("overtime_hours_100", 0.0) or pay_data.get("overtime_100_hours", 0.0)),
            "night_hours": float(pay_data.get("overtime_hours_night", 0.0) or pay_data.get("night_hours", 0.0)),
            "overtime_hours": float(pay_data.get("overtime_hours", 0.0)),
        },
        other_allowances={
            "advances": float(pay_data.get("advances", 0.0)),
            "other_deductions": float(pay_data.get("other_deductions", 0.0) or pay_data.get("deductions", 0.0)),
        },
        deductions_absences=float(pay_data.get("deduction_absences", 0.0)),
    )

    def _parse_date(val):
        if val is None:
            return None
        if isinstance(val, date):
            return val
        if isinstance(val, str):
            try:
                return datetime.strptime(val, "%Y-%m-%d").date()
            except Exception:
                return None
        return None

    p = PayrollEntry(
        employee_id=pay_data["employee_id"],
        employee_name=emp_name,
        department=dept,
        job_title=job,
        category=cat,
        period=pay_data.get("period") or f"{date.today().month:02d}/{date.today().year}",
        payroll_date=date.today(),
        base_salary=calc["base_salary"],
        bonus=calc["bonus_misc"],
        bonus_seniority=calc["bonus_seniority"],
        bonus_performance=calc["bonus_performance"],
        bonus_misc=calc["bonus_misc"],
        deduction_absences=calc["deduction_absences"],
        overtime_hours=calc["overtime_hours"],
        overtime_30_hours=calc["overtime_30_hours"],
        overtime_40_hours=calc["overtime_40_hours"],
        overtime_50_hours=calc["overtime_50_hours"],
        overtime_100_hours=calc["overtime_100_hours"],
        night_hours=calc["night_hours"],
        overtime_amount=calc["overtime_amount"],
        gross_salary=calc["gross_salary"],
        cnaps_employee=calc["cnaps_employee"],
        ostie_employee=calc["ostie_employee"],
        total_social_contributions=calc["total_social_contributions"],
        irsa=calc["irsa"],
        children_deduction=calc["children_deduction"],
        children_count=children_count,
        advances=calc["advances"],
        other_deductions=calc["other_deductions"],
        deductions=calc["deductions"],
        net_salary=calc["net_salary"],
        cnaps_employer=calc["cnaps_employer"],
        ostie_employer=calc["ostie_employer"],
        employer_charges=calc["employer_charges"],
        total_cost=calc["total_cost"],
        payment_status=pay_data.get("payment_status") or pay_data.get("status") or "CALCULE",
        payment_date=_parse_date(pay_data.get("payment_date")),
        payment_method=pay_data.get("payment_method"),
        notes=pay_data.get("notes"),
        created_by_user_id=pay_data.get("created_by_user_id"),
    )
    db.add(p)
    db.commit()
    db.refresh(p)

    log_action(
        db,
        action="CREATE",
        module="RH",
        target_entity=f"PAYROLL:{p.id_payroll}",
        details=f"Paie créée: {emp_name} période {p.period} - Net: {calc['net_salary']} Ar",
        new_values=_payroll_to_dict(p),
    )

    return _payroll_to_dict(p)


# ==============================================================================
# PERFORMANCE & COMPETENCES
# ==============================================================================

def get_performance_evaluations(db: Session) -> List[Dict[str, Any]]:
    items = db.query(PerformanceEvaluation).order_by(PerformanceEvaluation.created_at.desc()).all()
    return [_evaluation_to_dict(e) for e in items]


def create_performance_evaluation(db: Session, eval_data: Dict[str, Any]) -> Dict[str, Any]:
    emp = db.query(Employee).filter(Employee.id_employee == eval_data["employee_id"]).first()
    emp_name = f"{emp.first_name} {emp.last_name}" if emp else f"Employé #{eval_data['employee_id']}"
    dept = emp.department if emp else "Général"

    score = float(eval_data.get("overall_score") or eval_data.get("performance_score") or 0.0)
    if score >= 90.0:
        rating = "EXCELLENT"
    elif score >= 75.0:
        rating = "SATISFAISANT"
    else:
        rating = "A_AMELIORER"

    def _parse_date(val):
        if val is None:
            return None
        if isinstance(val, date):
            return val
        if isinstance(val, str):
            try:
                return datetime.strptime(val, "%Y-%m-%d").date()
            except Exception:
                return None
        return None

    def _to_json_field(val):
        if val is None:
            return None
        if isinstance(val, (dict, list)):
            try:
                return json.dumps(val, ensure_ascii=False)
            except Exception:
                return str(val)
        return str(val)

    e = PerformanceEvaluation(
        employee_id=eval_data["employee_id"],
        employee_name=emp_name,
        department=dept,
        evaluation_period=eval_data["evaluation_period"],
        evaluation_date=_parse_date(eval_data.get("evaluation_date")) or date.today(),
        performance_score=score,
        rating_label=rating,
        goals_achieved=_to_json_field(eval_data.get("goals_achieved") or eval_data.get("goals_json") or eval_data.get("achievements")),
        strengths=eval_data.get("strengths"),
        areas_to_improve=eval_data.get("areas_to_improve") or eval_data.get("areas_improvement"),
        skills=_to_json_field(eval_data.get("skills") or eval_data.get("skills_json")),
        training_recommended=eval_data.get("training_recommended") or eval_data.get("training_recommendations"),
        career_evolution_notes=eval_data.get("career_evolution_notes") or eval_data.get("notes"),
        evaluated_by_user_id=eval_data.get("evaluator_id") or eval_data.get("evaluated_by_user_id"),
        employee_signature=bool(eval_data.get("employee_signature", False)),
        manager_signature=bool(eval_data.get("evaluator_signature") or eval_data.get("manager_signature", False)),
        evaluated_at=datetime.now(timezone.utc),
    )
    db.add(e)
    db.commit()
    db.refresh(e)

    log_action(
        db,
        action="CREATE",
        module="RH",
        target_entity=f"EVALUATION:{e.id_evaluation}",
        details=f"Évaluation performance: {emp_name} période {e.evaluation_period} - Score {score} ({rating})",
        new_values=_evaluation_to_dict(e),
    )

    return _evaluation_to_dict(e)


# ==============================================================================
# OVERVIEW RH SYNTHETIQUE
# ==============================================================================

def get_hr_overview(db: Session) -> Dict[str, Any]:
    employees_all = db.query(Employee).all()
    active_emps = [e for e in employees_all if e.status == "ACTIF"]
    active_count = len(active_emps)
    total_count = len(employees_all)

    payrolls = db.query(PayrollEntry).all()
    total_gross_payroll = sum(p.gross_salary for p in payrolls)
    total_net_payroll = sum(p.net_salary for p in payrolls)
    total_employer_charges = sum(p.employer_charges for p in payrolls)
    avg_net_salary = round(total_net_payroll / active_count, 2) if active_count > 0 else 0.0

    time_offs = db.query(TimeOffRequest).all()
    accepted_leave = [t for t in time_offs if t.status == "ACCEPTE"]
    pending_leave = [t for t in time_offs if t.status == "EN_ATTENTE"]

    consumed_leave_days = sum(t.days_count for t in accepted_leave)
    annual_leave_total = active_count * PAYROLL_CONFIG["annual_leave_days"]
    remaining_leave_days = max(0, annual_leave_total - consumed_leave_days)

    working_days_per_year = 250
    absenteeism_rate = round(
        (consumed_leave_days / (active_count * working_days_per_year)) * 100, 2
    ) if active_count > 0 else 0.0

    departed = [e for e in employees_all if e.status in ("PARTI", "RETRAITE", "LICENCIE")]
    turnover_rate = round(
        (len(departed) / active_count) * 100, 2
    ) if active_count > 0 else 0.0

    evals = db.query(PerformanceEvaluation).all()
    avg_perf = round(
        sum(e.performance_score for e in evals) / len(evals), 1
    ) if evals else 0.0

    return {
        "total_employees": total_count,
        "active_employees": active_count,
        "total_gross_payroll": round(total_gross_payroll, 2),
        "total_net_payroll": round(total_net_payroll, 2),
        "total_employer_charges": round(total_employer_charges, 2),
        "average_net_salary": avg_net_salary,
        "pending_time_off_count": len(pending_leave),
        "consumed_leave_days": consumed_leave_days,
        "remaining_leave_days": remaining_leave_days,
        "annual_leave_entitlement": annual_leave_total,
        "absenteeism_rate_percent": absenteeism_rate,
        "turnover_rate_percent": turnover_rate,
        "average_performance_score": avg_perf,
    }


# ==============================================================================
# BACKWARD COMPAT: Empty in-memory store for purge functions (reset_all_business_data)
# ==============================================================================
_hr_store: Dict[str, List[Dict[str, Any]]] = {
    "employees": [],
    "time_off": [],
    "payrolls": [],
    "evaluations": []
}
