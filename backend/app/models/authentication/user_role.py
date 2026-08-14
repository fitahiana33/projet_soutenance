from sqlalchemy import Column, ForeignKey, Integer, Table

from app.core.database import Base


user_roles = Table(
    "user_roles",
    Base.metadata,
    Column(
        "id_user",
        Integer,
        ForeignKey("user_.id_user", ondelete="CASCADE"),
        primary_key=True
    ),
    Column(
        "id_role",
        Integer,
        ForeignKey("roles.id_role", ondelete="CASCADE"),
        primary_key=True
    )
)
