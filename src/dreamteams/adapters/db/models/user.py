from sqlalchemy import UUID, Boolean, Column, DateTime, Table, Text, func
from sqlalchemy.orm import composite, relationship

from dreamteams.adapters.db.models.base import mapper_registry
from dreamteams.entities.user import BanStatus, User

user_table = Table(
    "users",
    mapper_registry.metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("avatar", Text, nullable=True),
    Column("is_admin", Boolean, nullable=False, server_default="false"),
    Column("is_blocked", Boolean, nullable=False, server_default="false"),
    Column("blocked_reason", Text, nullable=True),
    Column("blocked_at", DateTime(timezone=True), nullable=True),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
)


mapper_registry.map_imperatively(
    User,
    user_table,
    properties={
        "ban_status": composite(
            BanStatus,
            user_table.c.is_blocked,
            user_table.c.blocked_reason,
            user_table.c.blocked_at,
        ),
        "organizer": relationship(
            "Organizer",
            lazy="raise_on_sql",
            cascade="all, delete-orphan",
            passive_deletes=True,
            uselist=False,
            back_populates="user",
        ),
        "participant": relationship(
            "Participant",
            lazy="raise_on_sql",
            cascade="all, delete-orphan",
            passive_deletes=True,
            uselist=False,
            back_populates="user",
        ),
    },
)
