from pydantic import BaseModel, ConfigDict


class PermissionBase(BaseModel):
    code: str
    description: str | None = None


class PermissionCreate(PermissionBase):
    pass


class PermissionUpdate(BaseModel):
    code: str | None = None
    description: str | None = None


class PermissionResponse(PermissionBase):
    id_permission: int

    model_config = ConfigDict(
        from_attributes=True
    )