from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.users.user import User
from app.api.deps import require_permission
from app.schemas.recruitment.recruitment import JobOfferCreate, JobOfferUpdate, CandidateCreate, RecruitmentMatchRequest
from app.services.recruitment.recruitment_service import (
    get_job_offers, create_job_offer, update_job_offer, update_job_offer_status, delete_job_offer,
    get_candidates, create_candidate, update_candidate_status,
    match_candidate_to_job, get_recruitment_overview
)
from app.services.audit.audit_service import log_action

router = APIRouter(prefix="/recruitment", tags=["Recrutement & Gestions des Talents"])


@router.get("/overview", summary="KPIs généraux du recrutement")
async def read_recruitment_overview(
    current_user: User = Depends(require_permission("HR_READ"))
):
    return await get_recruitment_overview()


@router.get("/jobs", summary="Liste des offres d'emploi ouvertes")
async def read_jobs(
    current_user: User = Depends(require_permission("HR_READ"))
):
    return await get_job_offers()


@router.post("/jobs", status_code=status.HTTP_201_CREATED, summary="Créer une offre d'emploi / fiche de poste")
async def add_job(
    data: JobOfferCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("HR_CREATE", "HR_MANAGE"))
):
    res = await create_job_offer(data.model_dump())
    log_action(
        db, action="CREATE", module="RH",
        user_id=current_user.id_user, username=current_user.username,
        target_entity=f"Offre {res['title']}", details=f"Département: {res['department']}"
    )
    return res


@router.put("/jobs/{job_id}", summary="Mettre à jour une offre d'emploi")
async def edit_job(
    job_id: int,
    data: JobOfferUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("HR_UPDATE", "HR_MANAGE"))
):
    try:
        res = await update_job_offer(job_id, data.model_dump(exclude_unset=True))
        log_action(
            db, action="UPDATE", module="RH",
            user_id=current_user.id_user, username=current_user.username,
            target_entity=f"Offre #{job_id}", details=f"Modification offre: {res['title']}"
        )
        return res
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/jobs/{job_id}/status", summary="Changer le statut d'une offre (OUVERT, EN_COURS, FERME)")
async def change_job_status(
    job_id: int,
    status_val: str = Query(..., alias="status", description="Nouveau statut (OUVERT, EN_COURS, FERME)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("HR_UPDATE", "HR_MANAGE"))
):
    try:
        res = await update_job_offer_status(job_id, status_val)
        log_action(
            db, action="UPDATE", module="RH",
            user_id=current_user.id_user, username=current_user.username,
            target_entity=f"Offre #{job_id}", details=f"Changement statut offre -> {status_val}"
        )
        return res
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/jobs/{job_id}", summary="Supprimer une offre d'emploi")
async def remove_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("HR_MANAGE"))
):
    try:
        await delete_job_offer(job_id)
        log_action(
            db, action="DELETE", module="RH",
            user_id=current_user.id_user, username=current_user.username,
            target_entity=f"Offre #{job_id}", details=f"Suppression offre d'emploi #{job_id}"
        )
        return {"success": True, "message": f"Offre d'emploi #{job_id} supprimée."}
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/candidates/{candidate_id}/status", summary="Changer le statut d'un candidat (EN_EVALUATION, ENTRETIEN, RETENU, REFUSE)")
async def change_candidate_status(
    candidate_id: int,
    status_val: str = Query(..., alias="status", description="Nouveau statut du candidat"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("HR_UPDATE", "HR_MANAGE"))
):
    try:
        res = await update_candidate_status(candidate_id, status_val)
        log_action(
            db, action="UPDATE", module="RH",
            user_id=current_user.id_user, username=current_user.username,
            target_entity=f"Candidat #{candidate_id}", details=f"Statut candidat -> {status_val}"
        )
        return res
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/candidates", summary="Banque de candidatures et CVs")
async def read_candidates(
    current_user: User = Depends(require_permission("HR_READ"))
):
    return await get_candidates()


@router.post("/candidates", status_code=status.HTTP_201_CREATED, summary="Enregistrer un candidat")
async def add_candidate(
    data: CandidateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("HR_CREATE", "HR_MANAGE"))
):
    res = await create_candidate(data.model_dump())
    log_action(
        db, action="CREATE", module="RH",
        user_id=current_user.id_user, username=current_user.username,
        target_entity=f"Candidat {res['first_name']} {res['last_name']}", details=f"Diplôme: {res['degree']}"
    )
    return res


@router.post("/match", summary="Matching compétences / poste avec scoring")
async def process_match(
    data: RecruitmentMatchRequest,
    current_user: User = Depends(require_permission("USER_READ"))
):
    try:
        return await match_candidate_to_job(data.job_offer_id, data.candidate_id)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
