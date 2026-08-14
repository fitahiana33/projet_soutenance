from sqlalchemy import Column, ForeignKey, Integer, Table

from app.core.database import Base


role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column(
        "id_role",
        Integer,
        ForeignKey("roles.id_role", ondelete="CASCADE"),
        primary_key=True
    ),
    Column(
        "id_permission",
        Integer,
        ForeignKey("permissions.id_permission", ondelete="CASCADE"),
        primary_key=True
    )
)
