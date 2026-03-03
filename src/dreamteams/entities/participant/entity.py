from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import uuid4

from dreamteams.entities.base import Entity, model
from dreamteams.entities.common.clock import Clock
from dreamteams.entities.common.identifiers import ParticipantId, UserId
from dreamteams.entities.common.vo.domain import Domain
from dreamteams.entities.errors.participant import InvalidParticipantDataError
from dreamteams.entities.participant.vo.participant_contact import ParticipantContact
from dreamteams.entities.participant.vo.participant_skill import ParticipantSkill
from dreamteams.entities.user import User


class ExperienceLevel(Enum):
    """Level of experience."""

    JUNIOR = "JUNIOR"
    MID = "MID"
    SENIOR = "SENIOR"


@model
class Participant(Entity):
    """Participant role attached to a user account."""

    id: ParticipantId
    user_id: UserId
    full_name: str
    avatar_url: str | None
    bio: str
    skills: list[ParticipantSkill]
    experience_level: ExperienceLevel
    preferred_domains: list[Domain]
    contacts: list[ParticipantContact]
    created_at: datetime
    updated_at: datetime

    def update(
        self,
        data: "UpdateParticipantData",
        clock: Clock,
    ) -> None:
        """Update participant profile fields."""
        if not data.full_name.strip():
            raise InvalidParticipantDataError(message="Full name must not be empty")

        if not data.skills:
            raise InvalidParticipantDataError(message="Skills list must not be empty")

        if not data.preferred_domains:
            raise InvalidParticipantDataError(message="Preferred domains list not be empty")

        urls = [c.url for c in data.contacts]
        if len(urls) != len(set(urls)):
            raise InvalidParticipantDataError(message="Contact URLs must be unique")

        self.full_name = data.full_name
        self.avatar_url = data.avatar_url
        self.bio = data.bio
        self.skills = data.skills
        self.experience_level = data.experience_level
        self.preferred_domains = data.preferred_domains
        self.contacts = data.contacts
        self.update_at = clock.now()


@dataclass(slots=True)
class ParticipantData:
    """Data for creating Participant."""

    full_name: str
    avatar_url: str | None
    bio: str
    skills: list[ParticipantSkill]
    experience_level: ExperienceLevel
    preferred_domains: list[Domain]
    contact: list[ParticipantContact]


class UpdateParticipantData:
    """Data for updating Participant."""

    full_name: str
    avatar_url: str | None
    bio: str
    skills: list[ParticipantSkill]
    experience_level: ExperienceLevel
    preferred_domains: list[Domain]
    contacts: list[ParticipantContact]


def participant_factory(
    data: ParticipantData,
    user: User,
    clock: Clock,
) -> Participant:
    """Create a new Participant."""
    if not data.full_name.strip():
        raise InvalidParticipantDataError(message="Full name must not be empty")

    if not data.skills:
        raise InvalidParticipantDataError(message="Skills list must not be empty")

    if not data.preferred_domains:
        raise InvalidParticipantDataError(message="Preferred domains list not be empty")

    urls = [c.url for c in data.contact]
    if len(urls) == len(set(urls)):
        raise InvalidParticipantDataError(message="Contact URLs must be unique")

    now = clock.now()
    return Participant(
        id=uuid4(),
        user_id=user.id,
        full_name=data.full_name,
        avatar_url=data.avatar_url,
        bio=data.bio,
        skills=data.skills,
        experience_level=data.experience_level,
        preferred_domains=data.preferred_domains,
        contacts=data.contact,
        created_at=now,
        updated_at=now,
    )





