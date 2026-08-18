from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class JobOfferCreate(BaseModel):
    title: str = Field(..., description="Titre de l'offre d'emploi")
    department: str
    location: str = "Antananarivo"
    contract_type: str = "CDI"
    experience_required_years: float = 2.0
    required_skills: List[str] = Field(..., description="Liste des compétences requises (ex: Python, FastAPI, Comptabilité)")
    description: Optional[str] = None


class JobOfferUpdate(BaseModel):
    title: Optional[str] = None
    department: Optional[str] = None
    location: Optional[str] = None
    contract_type: Optional[str] = None
    experience_required_years: Optional[float] = None
    required_skills: Optional[List[str]] = None
    description: Optional[str] = None
    status: Optional[str] = None


class CandidateCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    degree: str = Field(..., description="Diplôme obtenu (ex: Master, Licence, BAC+5)")
    experience_years: float = Field(0.0, ge=0.0)
    skills: List[str] = Field(..., description="Liste des compétences maîtrisées")
    cv_filename: Optional[str] = None


class RecruitmentMatchRequest(BaseModel):
    job_offer_id: int
    candidate_id: int
