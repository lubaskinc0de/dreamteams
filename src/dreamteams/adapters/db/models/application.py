from sqlalchemy import ARRAY, UUID, Column, DateTime, Enum, ForeignKey, Table, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB

from dreamteams.adapters.db.models.base import mapper_registry
from dreamteams.entities.application.entity import Application, ApplicationStatus
from dreamteams.entities.common.vo.domain import Domain

application_table = Table(
    "applications",
    mapper_registry.metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column(
        "participant_id",
        UUID(as_uuid=True),
        ForeignKey("participants.id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column(
        "competition_id",
        UUID(as_uuid=True),
        ForeignKey("competitions.id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column("domains", ARRAY(Enum(Domain, native_enum=False)), nullable=False),
    Column("status", Enum(ApplicationStatus, native_enum=False), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("form_data", JSONB, nullable=True),
    UniqueConstraint("participant_id", "competition_id", name="uq_applications_participant_competition"),
)

mapper_registry.map_imperatively(
    Application,
    application_table,
)
