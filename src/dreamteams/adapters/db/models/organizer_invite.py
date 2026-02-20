from sqlalchemy import UUID, Boolean, Column, DateTime, ForeignKey, String, Table, Text

from dreamteams.adapters.db.models.base import mapper_registry
from dreamteams.entities.organizer_invite import OrganizerInvite

organizer_invite_table = Table(
    "organizer_invite",
    mapper_registry.metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("code", String(64), nullable=False, unique=True),
    Column("display_name", Text, nullable=True),
    Column("created_by", UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
    Column("is_revoked", Boolean, nullable=False, server_default="false"),
    Column("is_used", Boolean, nullable=False, server_default="false"),
    Column("created_at", DateTime(timezone=True), nullable=False),
)


mapper_registry.map_imperatively(
    OrganizerInvite,
    organizer_invite_table,
)
