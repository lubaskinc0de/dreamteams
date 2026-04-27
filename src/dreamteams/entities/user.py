from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from uuid import uuid4

from dreamteams.entities.base import Entity, model
from dreamteams.entities.common.clock import Clock
from dreamteams.entities.common.identifiers import OrganizerId, ParticipantId, UserId
from dreamteams.entities.common.vo.domain import Domain
from dreamteams.entities.common.vo.participant_type import ParticipantType
from dreamteams.entities.errors.base import AccessDeniedError
from dreamteams.entities.errors.organizer import (
    OrganizerUserIdMismatchError,
)
from dreamteams.entities.errors.participant import (
    InvalidParticipantDataError,
    ParticipantUserIdMismatchError,
)
from dreamteams.entities.participant.vo.age import Age
from dreamteams.entities.participant.vo.participant_contacts import ParticipantContacts
from dreamteams.entities.participant.vo.participant_skills import ParticipantSkills

type Avatar = str


@dataclass(slots=True)
class BanStatus:
    """Value object representing the blocked state of a user account."""

    is_blocked: bool = False
    reason: str | None = None
    blocked_at: datetime | None = None


@model
class Organizer(Entity):
    """The organization that hosts competitions."""

    id: OrganizerId
    user_id: UserId
    user: "User"
    organizer_name: str
    phone_number: str
    contact_email: str

    def update(self, data: "UpdateOrganizerData") -> None:
        """Update organizer profile fields."""
        self.organizer_name = data.organizer_name
        self.contact_email = data.contact_email


@model
class User(Entity):
    """Domain entity representing a user in the application.

    Contains roles such as ``organizer`` and ``participant``.
    """

    id: UserId
    organizer: Organizer | None
    participant: "Participant | None" = None
    avatar: Avatar | None = None
    is_admin: bool = False
    ban_status: BanStatus = field(default_factory=BanStatus)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def block(self, admin: "User", reason: str | None, clock: Clock) -> None:
        """Block this user account. Admin only."""
        if not admin.is_admin:
            raise AccessDeniedError(message="Only admins can block users")
        self.ban_status = BanStatus(is_blocked=True, reason=reason, blocked_at=clock.now())

    def unblock(self, admin: "User") -> None:
        """Unblock this user account. Admin only."""
        if not admin.is_admin:
            raise AccessDeniedError(message="Only admins can unblock users")
        self.ban_status = BanStatus(is_blocked=False)

    def make_organizer(self, organizer: Organizer) -> None:
        """Attach ``Organizer`` role to user."""
        if organizer.user_id != self.id:
            raise OrganizerUserIdMismatchError

        self.organizer = organizer

    def make_participant(self, participant: "Participant") -> None:
        """Attach ``Participant`` role to user."""
        if participant.user_id != self.id:
            raise ParticipantUserIdMismatchError

        self.participant = participant

    def get_role(self) -> Organizer:
        """Get user role."""
        if self.organizer is not None:
            return self.organizer
        msg = "User has no attached role"
        raise ValueError(msg)


class ExperienceLevel(Enum):
    """Level of experience."""

    JUNIOR = "JUNIOR"
    MID = "MID"
    SENIOR = "SENIOR"


@dataclass
class UpdateOrganizerData:
    """Data for updating Organizer."""

    organizer_name: str
    contact_email: str


@dataclass
class UpdateParticipantData:
    """Data for updating Participant."""

    full_name: str
    bio: str | None
    skills: ParticipantSkills
    experience_level: ExperienceLevel | None
    preferred_domains: list[Domain]
    contacts: ParticipantContacts
    participant_type: ParticipantType
    age: Age


@dataclass
class ParticipantData:
    """Data for creating Participant."""

    full_name: str
    bio: str | None
    skills: ParticipantSkills
    experience_level: ExperienceLevel | None
    preferred_domains: list[Domain]
    contacts: ParticipantContacts
    participant_type: ParticipantType
    age: Age


@model
class Participant(Entity):
    """Participant role attached to a user account."""

    id: ParticipantId
    user_id: UserId
    full_name: str
    bio: str | None
    skills: ParticipantSkills
    experience_level: ExperienceLevel | None
    preferred_domains: list[Domain]
    contacts: ParticipantContacts
    participant_type: ParticipantType
    age: Age
    created_at: datetime
    updated_at: datetime

    def __post_init__(self) -> None:
        """Enforce Participant invariants on every construction and mutation."""
        if self.participant_type == ParticipantType.ANY:
            raise InvalidParticipantDataError(message="Participant type cannot be ANY")

    def update(
        self,
        data: "UpdateParticipantData",
        clock: Clock,
    ) -> None:
        """Update participant profile fields."""
        self.full_name = data.full_name
        self.bio = data.bio
        self.skills = ParticipantSkills(data.skills)
        self.experience_level = data.experience_level
        self.preferred_domains = data.preferred_domains
        self.participant_type = data.participant_type
        self.contacts = ParticipantContacts(data.contacts)
        self.age = data.age
        self.updated_at = clock.now()
        self.__post_init__()


def participant_factory(
    data: ParticipantData,
    user: User,
    clock: Clock,
) -> Participant:
    """Create a new Participant."""
    now = clock.now()
    return Participant(
        id=uuid4(),
        user_id=user.id,
        full_name=data.full_name,
        bio=data.bio,
        skills=ParticipantSkills(data.skills),
        experience_level=data.experience_level,
        preferred_domains=data.preferred_domains,
        contacts=ParticipantContacts(data.contacts),
        participant_type=data.participant_type,
        age=data.age,
        created_at=now,
        updated_at=now,
    )


def user_factory(user_id: UserId) -> User:
    """``User`` entity factory (user created without roles)."""
    return User(user_id, organizer=None, participant=None)
