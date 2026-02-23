from sqlalchemy import (
    ARRAY,
    UUID,
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    PrimaryKeyConstraint,
    String,
    Table,
    Text,
    asc,
)
from sqlalchemy.orm import composite, relationship

from dreamteams.adapters.db.models.base import mapper_registry
from dreamteams.entities.common.vo.domain import Domain
from dreamteams.entities.common.vo.participant_type import ParticipantType
from dreamteams.entities.competition.entity import Competition
from dreamteams.entities.competition.milestone import Milestone
from dreamteams.entities.competition.participant_limits import ParticipantLimits
from dreamteams.entities.competition.schedule import CompetitionSchedule
from dreamteams.entities.competition.team_size_range import TeamSizeRange
from dreamteams.entities.competition.venue import CompetitionFormat, CompetitionVenue
from dreamteams.entities.user import Organizer

competition_table = Table(
    "competitions",
    mapper_registry.metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("organizer_id", UUID(as_uuid=True), ForeignKey("organizer.id", ondelete="CASCADE"), nullable=False),
    Column("title", String(200), nullable=False),
    Column("banner", Text, nullable=True),
    Column("description", Text, nullable=False),
    Column("registration_start", DateTime(timezone=True), nullable=False),
    Column("registration_end", DateTime(timezone=True), nullable=False),
    Column("team_formation_start", DateTime(timezone=True), nullable=True),
    Column("team_formation_end", DateTime(timezone=True), nullable=True),
    Column("max_participants", Integer, nullable=False),
    Column("min_participants", Integer, nullable=False),
    Column("domains", ARRAY(Enum(Domain, native_enum=False)), nullable=False),
    Column("participant_type", Enum(ParticipantType, native_enum=False), nullable=False),
    Column("format", Enum(CompetitionFormat, native_enum=False), nullable=False),
    Column("location", Text, nullable=True),
    Column("max_team_size", Integer, nullable=False),
    Column("min_team_size", Integer, nullable=False),
    Column("is_archived", Boolean, nullable=False, default=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
)

milestone_table = Table(
    "milestones",
    mapper_registry.metadata,
    Column("competition_id", UUID(as_uuid=True), ForeignKey("competitions.id", ondelete="CASCADE"), nullable=False),
    Column("timestamp", DateTime(timezone=True), nullable=False),
    Column("title", String(200), nullable=False),
    PrimaryKeyConstraint("competition_id", "timestamp"),
)

mapper_registry.map_imperatively(
    Milestone,
    milestone_table,
)

mapper_registry.map_imperatively(
    Competition,
    competition_table,
    properties={
        "schedule": composite(
            CompetitionSchedule,
            competition_table.c.registration_start,
            competition_table.c.registration_end,
            competition_table.c.team_formation_start,
            competition_table.c.team_formation_end,
        ),
        "participant_limits": composite(
            ParticipantLimits,
            competition_table.c.max_participants,
            competition_table.c.min_participants,
        ),
        "venue": composite(
            CompetitionVenue,
            competition_table.c.format,
            competition_table.c.location,
        ),
        "team_size": composite(
            TeamSizeRange,
            competition_table.c.max_team_size,
            competition_table.c.min_team_size,
        ),
        "milestones": relationship(
            Milestone,
            foreign_keys=[milestone_table.c.competition_id],
            cascade="all, delete-orphan",
            lazy="selectin",
            order_by=asc(milestone_table.c.timestamp),
        ),
        "organizer": relationship(
            Organizer,
            lazy="selectin",
        ),
    },
)
