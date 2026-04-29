from typing import override

from sqlalchemy import (
    UUID,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    PrimaryKeyConstraint,
    String,
    Table,
    Text,
    TypeDecorator,
    asc,
)
from sqlalchemy.engine import Dialect
from sqlalchemy.orm import relationship

from dreamteams.adapters.db.models.base import mapper_registry
from dreamteams.entities.common.participant_type import ParticipantType
from dreamteams.entities.participant.age import Age
from dreamteams.entities.participant.participant_contact import ParticipantContact
from dreamteams.entities.participant.participant_contacts import ParticipantContacts
from dreamteams.entities.participant.participant_skill import ParticipantSkill, SkillLevel
from dreamteams.entities.participant.participant_skills import ParticipantSkills
from dreamteams.entities.user import ExperienceLevel, Participant, User


class AgeType(TypeDecorator[Age]):
    """SQLAlchemy type that maps between integer DB column and Age value object."""

    impl: type[Integer] = Integer  # type: ignore[mutable-override]
    cache_ok: bool = True  # type: ignore[mutable-override]

    @override
    def process_bind_param(self, value: Age | None, dialect: Dialect) -> int | None:
        """Convert Age VO to int for storage."""
        if isinstance(value, Age):
            return value.value
        return None

    @override
    def process_result_value(self, value: int | None, dialect: Dialect) -> Age | None:
        """Convert stored int back to Age VO."""
        if value is not None:
            return Age(value)
        return None


participant_table = Table(
    "participants",
    mapper_registry.metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
    Column("full_name", String(150), nullable=False),
    Column("bio", Text, nullable=True),
    Column("experience_level", Enum(ExperienceLevel, native_enum=False), nullable=True),
    Column("participant_type", Enum(ParticipantType, native_enum=False), nullable=False),
    Column("age", AgeType, nullable=False),
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
    Column("value", Text, nullable=False),
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
            lazy="raise_on_sql",
        ),
        "skills": relationship(
            ParticipantSkill,
            foreign_keys=[participant_skills_table.c.participant_id],
            collection_class=ParticipantSkills,
            cascade="all, delete-orphan",
            passive_deletes=True,
            lazy="raise_on_sql",
            order_by=asc(participant_skills_table.c.name),
        ),
        "contacts": relationship(
            ParticipantContact,
            foreign_keys=[participant_contacts_table.c.participant_id],
            collection_class=ParticipantContacts,
            cascade="all, delete-orphan",
            passive_deletes=True,
            lazy="raise_on_sql",
            order_by=asc(participant_contacts_table.c.title),
        ),
    },
)
