import logging
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.hr.holiday import PublicHoliday
from app.schemas.hr.holiday import HolidayCreate, HolidayUpdate

logger = logging.getLogger(__name__)


def get_all_holidays(db: Session) -> List[PublicHoliday]:
    """Récupère l'ensemble des jours fériés triés par date."""
    return db.query(PublicHoliday).order_by(PublicHoliday.date.asc()).all()


def get_holiday_by_id(db: Session, id_holiday: int) -> Optional[PublicHoliday]:
    """Récupère un jour férié par son ID."""
    return db.query(PublicHoliday).filter(PublicHoliday.id_holiday == id_holiday).first()


def create_holiday(db: Session, data: HolidayCreate) -> PublicHoliday:
    """Création d'un nouveau jour férié."""
    holiday = PublicHoliday(
        name=data.name,
        date=data.date,
        is_recurring=data.is_recurring,
        description=data.description
    )
    db.add(holiday)
    db.commit()
    db.refresh(holiday)
    logger.info(f"Jour férié créé: {holiday.name} ({holiday.date})")
    return holiday


def update_holiday(db: Session, id_holiday: int, data: HolidayUpdate) -> Optional[PublicHoliday]:
    """Mise à jour d'un jour férié existant."""
    holiday = get_holiday_by_id(db, id_holiday)
    if not holiday:
        return None

    if data.name is not None:
        holiday.name = data.name
    if data.date is not None:
        holiday.date = data.date
    if data.is_recurring is not None:
        holiday.is_recurring = data.is_recurring
    if data.description is not None:
        holiday.description = data.description

    db.commit()
    db.refresh(holiday)
    logger.info(f"Jour férié #{id_holiday} mis à jour: {holiday.name}")
    return holiday


def delete_holiday(db: Session, id_holiday: int) -> bool:
    """Suppression d'un jour férié."""
    holiday = get_holiday_by_id(db, id_holiday)
    if not holiday:
        return False

    db.delete(holiday)
    db.commit()
    logger.info(f"Jour férié #{id_holiday} supprimé.")
    return True
