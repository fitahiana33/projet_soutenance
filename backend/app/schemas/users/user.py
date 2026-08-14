from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from app.schemas.roles.role import RoleResponse


class UserBase(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    first_name: str | None = Field(
        default=None,
        max_length=50
    )
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(
        min_length=6,
        max_length=128
    )
    role_ids: list[int] | None = None


class UserUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=50
    )
    first_name: str | None = Field(
        default=None,
        max_length=50
    )
    email: EmailStr | None = None
    password: str | None = Field(
        default=None,
        min_length=6,
        max_length=128
    )
    is_active: bool | None = None
    role_ids: list[int] | None = None


class UserRoleAssign(BaseModel):
    role_ids: list[int]


class UserResponse(UserBase):
    id_user: int
    is_active: bool | None
    created_at: datetime | None
    updated_at: datetime | None
    last_login_at: datetime | None
    roles: list[RoleResponse] = []

    model_config = ConfigDict(
        from_attributes=True
    )
