from datetime import datetime

from pydantic import BaseModel

from dreamteams.entities.common.identifiers import OrganizerId, ParticipantId, UserId
from dreamteams.entities.common.vo.participant_type import ParticipantType
from dreamteams.entities.participant.vo.participant_contact import ParticipantContact
from dreamteams.entities.participant.vo.participant_skill import ParticipantSkill
from dreamteams.entities.user import BanStatus, ExperienceLevel


class AdminUserModel(BaseModel):
    """Admin-facing user account data."""

    id: UserId
    avatar_url: str | None
    is_admin: bool
    ban_status: BanStatus


class AdminOrganizerModel(BaseModel):
    """Admin-facing organizer profile data."""

    id: OrganizerId
    user_id: UserId
    organizer_name: str
    phone_number: str
    contact_email: str


class AdminParticipantModel(BaseModel):
    """Admin-facing participant profile data."""

    id: ParticipantId
    user_id: UserId
    full_name: str
    participant_type: ParticipantType
    age: int
    bio: str | None
    skills: list[ParticipantSkill]
    experience_level: ExperienceLevel | None
    contacts: list[ParticipantContact]
    created_at: datetime
    updated_at: datetime
