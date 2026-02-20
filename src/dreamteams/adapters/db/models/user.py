from sqlalchemy import UUID, Boolean, Column, Table, Text
from sqlalchemy.orm import relationship

from dreamteams.adapters.db.models.base import mapper_registry
from dreamteams.entities.user import User

user_table = Table(
    "users",
    mapper_registry.metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("avatar", Text, nullable=True),
    Column("is_admin", Boolean, nullable=False, server_default="false"),
)


mapper_registry.map_imperatively(
    User,
    user_table,
    properties={
        "organizer": relationship(
            "Organizer",
            lazy="selectin",
            cascade="all, delete-orphan",
            uselist=False,
            back_populates="user",
        ),
    },
)
