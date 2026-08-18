from datetime import date, datetime
from pydantic import BaseModel
from typing import Optional


class HolidayBase(BaseModel):
    name: str
    date: date
    is_recurring: bool = True
    description: Optional[str] = None


class HolidayCreate(HolidayBase):
    pass


class HolidayUpdate(BaseModel):
    name: Optional[str] = None
    date: Optional[date] = None
    is_recurring: Optional[bool] = None
    description: Optional[str] = None


class HolidayResponse(HolidayBase):
    id_holiday: int
    created_at: datetime

    class Config:
        from_attributes = True
