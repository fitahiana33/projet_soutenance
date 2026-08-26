from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_permission, require_active_user
from app.schemas.users.user import UserResponse
from app.schemas.hr.holiday import HolidayCreate, HolidayUpdate, HolidayResponse
from app.services.hr import holiday_service

router = APIRouter(prefix="/hr/holidays", tags=["HR & Public Holidays"])


@router.get("/", response_model=List[HolidayResponse], status_code=status.HTTP_200_OK)
def list_public_holidays(
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(require_active_user)
):
    """Récupère la liste des jours fériés légaux."""
    return holiday_service.get_all_holidays(db)


@router.post("/", response_model=HolidayResponse, status_code=status.HTTP_201_CREATED)
def create_public_holiday(
    payload: HolidayCreate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(require_permission("HOLIDAY_MANAGE", "HR_MANAGE"))
):
    """Création d'un nouveau jour férié."""
    return holiday_service.create_holiday(db, payload)


@router.put("/{id_holiday}", response_model=HolidayResponse, status_code=status.HTTP_200_OK)
def update_public_holiday(
    id_holiday: int,
    payload: HolidayUpdate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(require_permission("HOLIDAY_MANAGE", "HR_MANAGE"))
):
    """Modification d'un jour férié existant."""
    updated = holiday_service.update_holiday(db, id_holiday, payload)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Jour férié non trouvé.")
    return updated


@router.delete("/{id_holiday}", status_code=status.HTTP_200_OK)
def delete_public_holiday(
    id_holiday: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(require_permission("HOLIDAY_MANAGE", "HR_MANAGE"))
):
    """Suppression d'un jour férié."""
    success = holiday_service.delete_holiday(db, id_holiday)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Jour férié non trouvé.")
    return {"message": "Jour férié supprimé avec succès."}
