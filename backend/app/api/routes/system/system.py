from fastapi import APIRouter, Depends, status, HTTPException
from pydantic import BaseModel

from app.api.deps import get_current_user, require_permission
from app.schemas.users.user import UserResponse
from app.services.system import system_service

router = APIRouter(prefix="/system", tags=["System & Maintenance"])


class ResetDataRequest(BaseModel):
    confirm_text: str


@router.post("/reset-data", status_code=status.HTTP_200_OK)
async def reset_business_data(
    payload: ResetDataRequest,
    current_user: UserResponse = Depends(require_permission("PERMISSION_MANAGE"))
):
    """
    Réinitialise les données métiers.
    Nécessite la confirmation 'RESET' et la permission PERMISSION_MANAGE.
    """
    if payload.confirm_text.upper() != "RESET":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Texte de confirmation incorrect. Saisissez 'RESET' pour valider."
        )

    return await system_service.reset_all_business_data()
