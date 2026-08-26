from typing import List, Optional
from fastapi import APIRouter, Depends, status, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, require_permission
from app.schemas.users.user import UserResponse
from app.schemas.system.parameter import ParameterCreate, ParameterUpdate, ParameterResponse
from app.services.system import system_service

router = APIRouter(prefix="/system", tags=["System & Maintenance"])


class ResetDataRequest(BaseModel):
    confirm_text: str


@router.get("/parameters", status_code=status.HTTP_200_OK)
def read_business_parameters(
    raw: bool = Query(False, description="Si true, renvoie la liste d'objets SystemParameter, sinon le dictionnaire de valeurs."),
    category: Optional[str] = Query(None, description="Filtrer par catégorie"),
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(require_permission("SYSTEM_READ"))
):
    """Récupère les paramètres métiers système configurés dans PostgreSQL."""
    if raw:
        return system_service.get_db_parameters(db, category)
    return system_service.get_business_parameters(db)


@router.post("/parameters", response_model=ParameterResponse, status_code=status.HTTP_201_CREATED)
def create_system_parameter(
    payload: ParameterCreate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(require_permission("SYSTEM_MANAGE"))
):
    """Création d'un nouveau paramètre système dans PostgreSQL."""
    existing = system_service.get_parameter_by_key(db, payload.key)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Un paramètre avec la clé '{payload.key}' existe déjà.")
    return system_service.create_parameter(db, payload)


@router.put("/parameters/{id_param}", response_model=ParameterResponse, status_code=status.HTTP_200_OK)
def update_system_parameter(
    id_param: int,
    payload: ParameterUpdate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(require_permission("SYSTEM_MANAGE"))
):
    """Modification d'un paramètre système existant dans PostgreSQL."""
    updated = system_service.update_parameter(db, id_param, payload)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paramètre non trouvé.")
    return updated


@router.delete("/parameters/{id_param}", status_code=status.HTTP_200_OK)
def delete_system_parameter(
    id_param: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(require_permission("SYSTEM_MANAGE"))
):
    """Suppression d'un paramètre système de PostgreSQL."""
    success = system_service.delete_parameter(db, id_param)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paramètre non trouvé.")
    return {"message": "Paramètre supprimé avec succès."}


@router.put("/parameters", status_code=status.HTTP_200_OK)
def bulk_modify_business_parameters(
    payload: dict,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(require_permission("SYSTEM_MANAGE"))
):
    """Met à jour les paramètres métiers par lots dans PostgreSQL."""
    return system_service.bulk_update_parameters(db, payload)


@router.post("/reset-data", status_code=status.HTTP_200_OK)
async def reset_business_data(
    payload: ResetDataRequest,
    current_user: UserResponse = Depends(require_permission("SYSTEM_MANAGE"))
):
    """
    Réinitialise les données métiers.
    Nécessite la confirmation 'RESET' et la permission SYSTEM_MANAGE.
    """
    if payload.confirm_text.upper() != "RESET":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Texte de confirmation incorrect. Saisissez 'RESET' pour valider."
        )

    return await system_service.reset_all_business_data()
