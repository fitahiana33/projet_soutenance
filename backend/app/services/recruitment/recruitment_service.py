import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.hr.recruitment import JobOffer, Candidate, CandidateEvaluation, CandidateInterview
from app.models.hr.employee import Employee

logger = logging.getLogger(__name__)


def _job_to_dict(j: JobOffer) -> Dict[str, Any]:
    return {
        "id_job": j.id_job,
        "title": j.title,
        "department": j.department,
        "location": j.location,
        "contract_type": j.contract_type,
        "experience_required_years": j.experience_required_years,
        "required_skills": j.required_skills or [],
        "description": j.description,
        "status": j.status,
        "created_at": j.created_at.isoformat() if j.created_at else None,
        "updated_at": j.updated_at.isoformat() if j.updated_at else None,
    }


def _candidate_to_dict(c: Candidate) -> Dict[str, Any]:
    return {
        "id_candidate": c.id_candidate,
        "first_name": c.first_name,
        "last_name": c.last_name,
        "email": c.email,
        "phone": c.phone,
        "degree": c.degree,
        "experience_years": c.experience_years,
        "skills": c.skills or [],
        "cv_filename": c.cv_filename,
        "job_offer_id": c.job_offer_id,
        "matching_score": c.matching_score,
        "final_decision": c.final_decision,
        "validated_by_user_id": c.validated_by_user_id,
        "validated_at": c.validated_at.isoformat() if c.validated_at else None,
        "employee_id": c.employee_id,
        "evaluations": [{"id_evaluation": e.id_evaluation, "score": e.score, "strengths": e.strengths, "weaknesses": e.weaknesses, "comments": e.comments, "created_at": e.created_at.isoformat() if e.created_at else None} for e in c.evaluations],
        "interviews": [{"id_interview": i.id_interview, "scheduled_at": i.scheduled_at.isoformat() if i.scheduled_at else None, "status": i.status, "feedback": i.feedback, "score": i.score} for i in c.interviews],
        "status": c.status,
        "created_at": c.created_at.isoformat() if c.created_at else None,
        "updated_at": c.updated_at.isoformat() if c.updated_at else None,
    }


async def get_job_offers(db: Optional[Session] = None) -> List[Dict[str, Any]]:
    """Récupère la liste des offres d'emploi depuis PostgreSQL."""
    session_owner = False
    if db is None:
        db = SessionLocal()
        session_owner = True
    try:
        jobs = db.query(JobOffer).order_by(JobOffer.id_job.asc()).all()
        return [_job_to_dict(j) for j in jobs]
    finally:
        if session_owner:
            db.close()


async def create_job_offer(job_data: Dict[str, Any], db: Optional[Session] = None) -> Dict[str, Any]:
    """Création d'une nouvelle offre d'emploi / fiche de poste dans PostgreSQL."""
    session_owner = False
    if db is None:
        db = SessionLocal()
        session_owner = True
    try:
        new_job = JobOffer(
            title=job_data["title"],
            department=job_data["department"],
            location=job_data.get("location", "Antananarivo"),
            contract_type=job_data.get("contract_type", "CDI"),
            experience_required_years=float(job_data.get("experience_required_years", 2.0)),
            required_skills=job_data.get("required_skills", []),
            description=job_data.get("description", ""),
            status=job_data.get("status", "OUVERT")
        )
        db.add(new_job)
        db.commit()
        db.refresh(new_job)
        return _job_to_dict(new_job)
    finally:
        if session_owner:
            db.close()


async def update_job_offer(id_job: int, update_data: Dict[str, Any], db: Optional[Session] = None) -> Dict[str, Any]:
    """Mise à jour d'une offre d'emploi existante dans PostgreSQL."""
    session_owner = False
    if db is None:
        db = SessionLocal()
        session_owner = True
    try:
        job = db.query(JobOffer).filter(JobOffer.id_job == id_job).first()
        if not job:
            raise RuntimeError(f"Offre d'emploi #{id_job} non trouvée.")

        for k, v in update_data.items():
            if v is not None and hasattr(job, k):
                setattr(job, k, v)

        db.commit()
        db.refresh(job)
        return _job_to_dict(job)
    finally:
        if session_owner:
            db.close()


async def update_job_offer_status(id_job: int, status_val: str, db: Optional[Session] = None) -> Dict[str, Any]:
    """Changer le statut d'une offre (OUVERT, EN_COURS, FERME)."""
    return await update_job_offer(id_job, {"status": status_val}, db=db)


async def delete_job_offer(id_job: int, db: Optional[Session] = None) -> bool:
    """Suppression d'une offre d'emploi dans PostgreSQL."""
    session_owner = False
    if db is None:
        db = SessionLocal()
        session_owner = True
    try:
        job = db.query(JobOffer).filter(JobOffer.id_job == id_job).first()
        if not job:
            raise RuntimeError(f"Offre d'emploi #{id_job} non trouvée.")
        db.delete(job)
        db.commit()
        return True
    finally:
        if session_owner:
            db.close()


async def get_candidates(db: Optional[Session] = None) -> List[Dict[str, Any]]:
    """Récupère la banque de candidatures depuis PostgreSQL."""
    session_owner = False
    if db is None:
        db = SessionLocal()
        session_owner = True
    try:
        cands = db.query(Candidate).order_by(Candidate.id_candidate.asc()).all()
        return [_candidate_to_dict(c) for c in cands]
    finally:
        if session_owner:
            db.close()


async def get_candidate_by_id(id_candidate: int, db: Optional[Session] = None) -> Optional[Dict[str, Any]]:
    """Recupere la fiche complete d'un candidat."""
    session_owner = False
    if db is None:
        db = SessionLocal()
        session_owner = True
    try:
        cand = db.query(Candidate).filter(Candidate.id_candidate == id_candidate).first()
        return _candidate_to_dict(cand) if cand else None
    finally:
        if session_owner:
            db.close()


async def create_candidate(cand_data: Dict[str, Any], db: Optional[Session] = None) -> Dict[str, Any]:
    """Enregistrement d'un nouveau candidat dans PostgreSQL."""
    session_owner = False
    if db is None:
        db = SessionLocal()
        session_owner = True
    try:
        new_cand = Candidate(
            first_name=cand_data["first_name"],
            last_name=cand_data["last_name"],
            email=cand_data["email"],
            phone=cand_data.get("phone", ""),
            degree=cand_data["degree"],
            experience_years=float(cand_data.get("experience_years", 0.0)),
            skills=cand_data.get("skills", []),
            cv_filename=cand_data.get("cv_filename"),
            job_offer_id=cand_data.get("job_offer_id"),
            status=cand_data.get("status", "EN_EVALUATION")
        )
        db.add(new_cand)
        db.commit()
        db.refresh(new_cand)
        return _candidate_to_dict(new_cand)
    finally:
        if session_owner:
            db.close()


async def update_candidate_status(id_candidate: int, status_val: str, db: Optional[Session] = None) -> Dict[str, Any]:
    """Changer le statut d'une candidature dans PostgreSQL."""
    session_owner = False
    if db is None:
        db = SessionLocal()
        session_owner = True
    try:
        cand = db.query(Candidate).filter(Candidate.id_candidate == id_candidate).first()
        if not cand:
            raise RuntimeError(f"Candidat #{id_candidate} non trouvé.")
        cand.status = status_val
        db.commit()
        db.refresh(cand)
        return _candidate_to_dict(cand)
    finally:
        if session_owner:
            db.close()


async def add_candidate_evaluation(id_candidate: int, data: Dict[str, Any], user_id: int, db: Session) -> Dict[str, Any]:
    cand = db.query(Candidate).filter(Candidate.id_candidate == id_candidate).first()
    if not cand:
        raise RuntimeError(f"Candidat #{id_candidate} non trouvé.")
    db.add(CandidateEvaluation(candidate_id=id_candidate, evaluator_user_id=user_id, **data))
    cand.status = "EN_EVALUATION"
    cand.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(cand)
    return _candidate_to_dict(cand)


async def add_candidate_interview(id_candidate: int, data: Dict[str, Any], user_id: int, db: Session) -> Dict[str, Any]:
    cand = db.query(Candidate).filter(Candidate.id_candidate == id_candidate).first()
    if not cand:
        raise RuntimeError(f"Candidat #{id_candidate} non trouvé.")
    db.add(CandidateInterview(candidate_id=id_candidate, interviewer_user_id=user_id, **data))
    cand.status = "ENTRETIEN"
    cand.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(cand)
    return _candidate_to_dict(cand)


async def decide_candidate(id_candidate: int, decision: str, user_id: int, db: Session) -> Dict[str, Any]:
    cand = db.query(Candidate).filter(Candidate.id_candidate == id_candidate).first()
    if not cand:
        raise RuntimeError(f"Candidat #{id_candidate} non trouvé.")
    if not cand.evaluations and not cand.interviews:
        raise RuntimeError("Une évaluation ou un entretien est requis avant la décision finale.")
    cand.final_decision = decision
    cand.status = decision if decision != "EN_ATTENTE" else "EN_EVALUATION"
    cand.validated_by_user_id = user_id
    cand.validated_at = datetime.now(timezone.utc)
    cand.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(cand)
    return _candidate_to_dict(cand)


async def create_employee_from_candidate(id_candidate: int, data: Dict[str, Any], user_id: int, db: Session) -> Dict[str, Any]:
    cand = db.query(Candidate).filter(Candidate.id_candidate == id_candidate).first()
    if not cand:
        raise RuntimeError(f"Candidat #{id_candidate} non trouvé.")
    if cand.final_decision != "RETENU" or not cand.validated_by_user_id:
        raise RuntimeError("La candidature doit être retenue et validée avant de créer un employé.")
    if cand.employee_id:
        raise RuntimeError("Un employé est déjà lié à cette candidature.")
    employee = Employee(
        matricule=f"EMP-2026-{db.query(Employee).count() + 1:03d}", first_name=cand.first_name,
        last_name=cand.last_name, email=cand.email, phone=cand.phone,
        department=data["department"], job_title=data["job_title"],
        contract_type=data.get("contract_type", "CDI"),
        hire_date=datetime.strptime(data["hire_date"], "%Y-%m-%d").date(),
        base_salary=data["base_salary"], status="ACTIF"
    )
    db.add(employee)
    db.flush()
    cand.employee_id = employee.id_employee
    cand.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(cand)
    return _candidate_to_dict(cand)


def calculate_matching_score(job: Dict[str, Any], candidate: Dict[str, Any]) -> Dict[str, Any]:
    """
    Algorithme de matching profil / poste transparent :
    - 70% : Taux de correspondance des compétences clés exigées
    - 30% : Adéquation des années d'expérience
    """
    req_skills = [s.strip().lower() for s in job.get("required_skills", [])]
    cand_skills = [s.strip().lower() for s in candidate.get("skills", [])]

    if not req_skills:
        skill_score = 100.0
        validated_skills = cand_skills
        missing_skills = []
    else:
        matched = [s for s in req_skills if s in cand_skills]
        skill_score = (len(matched) / len(req_skills)) * 100.0
        validated_skills = [s for s in job.get("required_skills", []) if s.strip().lower() in matched]
        missing_skills = [s for s in job.get("required_skills", []) if s.strip().lower() not in matched]

    req_exp = float(job.get("experience_required_years", 1.0))
    cand_exp = float(candidate.get("experience_years", 0.0))
    exp_ratio = min(1.0, cand_exp / req_exp) if req_exp > 0 else 1.0
    exp_score = exp_ratio * 100.0

    total_score = round((skill_score * 0.70) + (exp_score * 0.30), 1)

    if total_score >= 85.0:
        recommendation = "EXCELLENT_MATCH"
    elif total_score >= 65.0:
        recommendation = "BON_PROFIL"
    else:
        recommendation = "ECARTS_COMPETENCES"

    return {
        "job_title": job["title"],
        "candidate_name": f"{candidate['first_name']} {candidate['last_name']}",
        "matching_score_percent": total_score,
        "recommendation": recommendation,
        "skills_match_score": round(skill_score, 1),
        "experience_match_score": round(exp_score, 1),
        "validated_skills": validated_skills,
        "missing_skills": missing_skills,
        "candidate_experience_years": cand_exp,
        "required_experience_years": req_exp
    }


async def match_candidate_to_job(job_id: int, candidate_id: int, db: Optional[Session] = None) -> Dict[str, Any]:
    """Exécute l'analyse de correspondance entre un candidat et une offre d'emploi."""
    jobs = await get_job_offers(db)
    cands = await get_candidates(db)

    job = next((j for j in jobs if j["id_job"] == job_id), None)
    cand = next((c for c in cands if c["id_candidate"] == candidate_id), None)

    if not job or not cand:
        raise RuntimeError("Offre d'emploi ou Candidat introuvable.")

    result = calculate_matching_score(job, cand)
    if db is not None:
        candidate_row = db.query(Candidate).filter(Candidate.id_candidate == candidate_id).first()
        if candidate_row:
            candidate_row.job_offer_id = job_id
            candidate_row.matching_score = result["matching_score_percent"]
            candidate_row.updated_at = datetime.now(timezone.utc)
            db.commit()
    return result


async def get_recruitment_overview(db: Optional[Session] = None) -> Dict[str, Any]:
    """KPIs généraux du module Recrutement."""
    jobs = await get_job_offers(db)
    cands = await get_candidates(db)

    open_jobs = sum(1 for j in jobs if j["status"] == "OUVERT")

    return {
        "total_job_offers": len(jobs),
        "open_job_offers_count": open_jobs,
        "total_candidates_count": len(cands),
        "average_candidates_per_job": round(len(cands) / len(jobs), 1) if jobs else 0.0
    }
