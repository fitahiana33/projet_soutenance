from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class ParameterBase(BaseModel):
    category: str
    key: str
    value: str
    label: str
    description: Optional[str] = None


class ParameterCreate(ParameterBase):
    pass


class ParameterUpdate(BaseModel):
    category: Optional[str] = None
    key: Optional[str] = None
    value: Optional[str] = None
    label: Optional[str] = None
    description: Optional[str] = None


class ParameterResponse(ParameterBase):
    id_param: int
    updated_at: datetime

    class Config:
        from_attributes = True
