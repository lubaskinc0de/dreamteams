from sqlalchemy import UUID, Column, ForeignKey, String, Table, Text

from dreamteams.adapters.db.models.base import mapper_registry
from dreamteams.entities.organizer import Organizer

organizer_table = Table(
    "organizer",
    mapper_registry.metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
    Column("organizer_name", String(150), nullable=False),
    Column("phone_number", String(100), nullable=False, unique=True),
    Column("contact_email", Text, nullable=False, unique=True),
    Column("logo", Text, nullable=True),
)


mapper_registry.map_imperatively(
    Organizer,
    organizer_table,
)
