from pydantic import BaseModel, ConfigDict
from app.schemas.permissions.permission import PermissionResponse


class RoleBase(BaseModel):
    libelle: str
    description: str | None = None


class RoleCreate(RoleBase):
    permission_ids: list[int] | None = None


class RoleUpdate(BaseModel):
    libelle: str | None = None
    description: str | None = None
    permission_ids: list[int] | None = None


class RolePermissionAssign(BaseModel):
    permission_ids: list[int]


class RoleResponse(RoleBase):
    id_role: int
    permissions: list[PermissionResponse] = []

    model_config = ConfigDict(
        from_attributes=True
    )