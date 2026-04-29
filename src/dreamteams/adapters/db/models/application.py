from sqlalchemy import UUID, Column, DateTime, Enum, ForeignKey, String, Table, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import composite

from dreamteams.adapters.db.models.base import mapper_registry
from dreamteams.entities.application.entity import Application, ApplicationStatus
from dreamteams.entities.competition.track import CompetitionTrack

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
    Column("track_name", String(100), nullable=False),
    Column("status", Enum(ApplicationStatus, native_enum=False), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("form_data", JSONB, nullable=True),
    UniqueConstraint("participant_id", "competition_id", name="uq_applications_participant_competition"),
)

mapper_registry.map_imperatively(
    Application,
    application_table,
    properties={
        "track": composite(
            CompetitionTrack,
            application_table.c.track_name,
        ),
    },
)
