import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# Primary in-memory store for HR Module
_hr_store: Dict[str, List[Dict[str, Any]]] = {
    "employees": [],
    "time_off": [],
    "payrolls": [],
    "evaluations": []
}


def _calculate_seniority(hire_date_str: str) -> tuple[int, str]:
    """Calcule l'ancienneté en mois et formate un libellé lisible."""
    try:
        hire_dt = datetime.strptime(hire_date_str, "%Y-%m-%d")
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


# --- EMPLOYES ---

async def get_all_employees() -> List[Dict[str, Any]]:
    """Récupère la liste des salariés avec calcul d'ancienneté."""
    result = []
    for emp in _hr_store["employees"]:
        months, label = _calculate_seniority(emp["hire_date"])
        item = {**emp, "seniority_months": months, "seniority_label": label}
        result.append(item)
    return result


async def create_employee(emp_data: Dict[str, Any]) -> Dict[str, Any]:
    """Création d'une nouvelle fiche salarié."""
    new_id = len(_hr_store["employees"]) + 1
    mat = emp_data.get("matricule") or f"EMP-2026-{new_id:03d}"

    item = {
        "id_employee": new_id,
        "matricule": mat,
        "first_name": emp_data["first_name"],
        "last_name": emp_data["last_name"],
        "email": emp_data["email"],
        "phone": emp_data.get("phone", ""),
        "department": emp_data["department"],
        "job_title": emp_data["job_title"],
        "contract_type": emp_data.get("contract_type", "CDI"),
        "hire_date": emp_data["hire_date"],
        "base_salary": float(emp_data["base_salary"]),
        "status": emp_data.get("status", "ACTIF"),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    _hr_store["employees"].append(item)

    months, label = _calculate_seniority(item["hire_date"])
    return {**item, "seniority_months": months, "seniority_label": label}


# --- TEMPS ET ABSENCES ---

async def get_time_off_requests() -> List[Dict[str, Any]]:
    """Récupère les demandes de congés et absences."""
    return _hr_store["time_off"]


async def create_time_off_request(req_data: Dict[str, Any]) -> Dict[str, Any]:
    """Création d'une nouvelle demande de congé / absence."""
    employees = await get_all_employees()
    emp = next((e for e in employees if e["id_employee"] == req_data["employee_id"]), None)

    new_id = len(_hr_store["time_off"]) + 1
    item = {
        "id_time_off": new_id,
        "employee_id": req_data["employee_id"],
        "employee_name": f"{emp['first_name']} {emp['last_name']}" if emp else f"Employé #{req_data['employee_id']}",
        "department": emp["department"] if emp else "Général",
        "leave_type": req_data.get("leave_type", "PAYE"),
        "start_date": req_data["start_date"],
        "end_date": req_data["end_date"],
        "days_count": float(req_data["days_count"]),
        "reason": req_data.get("reason", ""),
        "status": "EN_ATTENTE",
        "requested_at": datetime.now(timezone.utc).isoformat()
    }
    _hr_store["time_off"].append(item)
    return item


async def validate_time_off_request(id_time_off: int, action: str, comment: Optional[str] = None) -> Dict[str, Any]:
    """Validation ou Rejet d'une demande de congé."""
    to = next((t for t in _hr_store["time_off"] if t["id_time_off"] == id_time_off), None)
    if not to:
        raise RuntimeError(f"Demande de congé #{id_time_off} non trouvée.")

    if action.upper() in ["ACCEPTER", "VALIDER"]:
        to["status"] = "ACCEPTE"
    elif action.upper() in ["REFUSER", "REJETER"]:
        to["status"] = "REFUSE"
        if comment:
            to["reason"] = f"{to.get('reason', '')} | Motif refus: {comment}"
    else:
        raise ValueError("Action invalide.")

    return to


# --- GESTION DE LA PAIE ---

async def get_payrolls() -> List[Dict[str, Any]]:
    """Récupère l'historique des fiches de paie."""
    return _hr_store["payrolls"]


async def create_payroll(pay_data: Dict[str, Any]) -> Dict[str, Any]:
    """Génération d'une fiche de paie avec calculs automatiques Brut/Deductions/Net."""
    employees = await get_all_employees()
    emp = next((e for e in employees if e["id_employee"] == pay_data["employee_id"]), None)

    gross = float(pay_data["gross_salary"])
    bonus = float(pay_data.get("bonus", 0.0))
    ot_amount = float(pay_data.get("overtime_amount", 0.0))

    # Estimation standard des charges et retenues si non précisées
    deductions = float(pay_data.get("deductions") or round(gross * 0.22, 2))
    charges = float(pay_data.get("employer_charges") or round(gross * 0.40, 2))

    net = round(gross + bonus + ot_amount - deductions, 2)

    new_id = len(_hr_store["payrolls"]) + 1
    item = {
        "id_payroll": new_id,
        "employee_id": pay_data["employee_id"],
        "employee_name": f"{emp['first_name']} {emp['last_name']}" if emp else f"Employé #{pay_data['employee_id']}",
        "department": emp["department"] if emp else "Général",
        "job_title": emp["job_title"] if emp else "Poste",
        "period": pay_data["period"],
        "gross_salary": gross,
        "bonus": bonus,
        "overtime_hours": float(pay_data.get("overtime_hours", 0.0)),
        "overtime_amount": ot_amount,
        "deductions": deductions,
        "net_salary": net,
        "employer_charges": charges,
        "payment_status": "PAYE",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    _hr_store["payrolls"].append(item)
    return item


# --- PERFORMANCE & COMPETENCES ---

async def get_performance_evaluations() -> List[Dict[str, Any]]:
    """Récupère la liste des évaluations de performance."""
    return _hr_store["evaluations"]


async def create_performance_evaluation(eval_data: Dict[str, Any]) -> Dict[str, Any]:
    """Saisie d'une évaluation de performance et bilan de compétences."""
    employees = await get_all_employees()
    emp = next((e for e in employees if e["id_employee"] == eval_data["employee_id"]), None)

    score = float(eval_data["performance_score"])
    if score >= 90.0:
        rating = "EXCELLENT"
    elif score >= 75.0:
        rating = "SATISFAISANT"
    else:
        rating = "A_AMELIORER"

    new_id = len(_hr_store["evaluations"]) + 1
    item = {
        "id_evaluation": new_id,
        "employee_id": eval_data["employee_id"],
        "employee_name": f"{emp['first_name']} {emp['last_name']}" if emp else f"Employé #{eval_data['employee_id']}",
        "department": emp["department"] if emp else "Général",
        "evaluation_period": eval_data["evaluation_period"],
        "performance_score": score,
        "goals_achieved": eval_data["goals_achieved"],
        "skills": eval_data.get("skills", []),
        "training_recommended": eval_data.get("training_recommended", ""),
        "career_evolution_notes": eval_data.get("career_evolution_notes", ""),
        "rating_label": rating,
        "evaluated_at": datetime.now(timezone.utc).isoformat()
    }
    _hr_store["evaluations"].append(item)
    return item


# --- OVERVIEW RH SYNTHETIQUE ---

async def get_hr_overview() -> Dict[str, Any]:
    """KPIs globaux du module Ressources Humaines."""
    employees = await get_all_employees()
    time_off = _hr_store["time_off"]
    payrolls = _hr_store["payrolls"]
    evals = _hr_store["evaluations"]

    total_net_payroll = sum(p["net_salary"] for p in payrolls)
    pending_time_off = sum(1 for t in time_off if t["status"] == "EN_ATTENTE")

    avg_perf = round(sum(e["performance_score"] for e in evals) / len(evals), 1) if evals else 85.0

    return {
        "total_employees": len(employees),
        "total_net_payroll_monthly": round(total_net_payroll, 2),
        "pending_time_off_count": pending_time_off,
        "average_performance_score": avg_perf
    }
