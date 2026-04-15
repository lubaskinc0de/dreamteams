from sqlalchemy import (
    ARRAY,
    UUID,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    PrimaryKeyConstraint,
    String,
    Table,
    Text,
)
from sqlalchemy.orm import relationship

from dreamteams.adapters.db.models.base import mapper_registry
from dreamteams.entities.common.vo.domain import Domain
from dreamteams.entities.common.vo.participant_type import ParticipantType
from dreamteams.entities.participant.vo.participant_contact import ParticipantContact
from dreamteams.entities.participant.vo.participant_skill import ParticipantSkill, SkillLevel
from dreamteams.entities.user import ExperienceLevel, Participant, User

participant_table = Table(
    "participants",
    mapper_registry.metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
    Column("full_name", String(150), nullable=False),
    Column("bio", Text, nullable=False),
    Column("experience_level", Enum(ExperienceLevel, native_enum=False), nullable=False),
    Column("preferred_domains", ARRAY(Enum(Domain, native_enum=False)), nullable=False),
    Column("participant_type", Enum(ParticipantType, native_enum=False), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
)

participant_skills_table = Table(
    "participant_skills",
    mapper_registry.metadata,
    Column("participant_id", UUID(as_uuid=True), ForeignKey("participants.id", ondelete="CASCADE"), nullable=False),
    Column("name", String(70), nullable=False),
    Column("level", Enum(SkillLevel, native_enum=False), nullable=False),
    PrimaryKeyConstraint("participant_id", "name"),
)

participant_contacts_table = Table(
    "participant_contacts",
    mapper_registry.metadata,
    Column("participant_id", UUID(as_uuid=True), ForeignKey("participants.id", ondelete="CASCADE"), nullable=False),
    Column("title", String(70), nullable=False),
    Column("url", Text, nullable=False),
    PrimaryKeyConstraint("participant_id", "title"),
)

mapper_registry.map_imperatively(
    ParticipantSkill,
    participant_skills_table,
)

mapper_registry.map_imperatively(
    ParticipantContact,
    participant_contacts_table,
)

mapper_registry.map_imperatively(
    Participant,
    participant_table,
    properties={
        "user": relationship(
            User,
            back_populates="participant",
            lazy="selectin",
        ),
        "skills": relationship(
            ParticipantSkill,
            foreign_keys=[participant_skills_table.c.participant_id],
            cascade="all, delete-orphan",
            lazy="selectin",
        ),
        "contacts": relationship(
            ParticipantContact,
            foreign_keys=[participant_contacts_table.c.participant_id],
            cascade="all, delete-orphan",
            lazy="selectin",
        ),
    },
)
