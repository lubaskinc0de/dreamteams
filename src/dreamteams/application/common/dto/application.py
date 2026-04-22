from datetime import datetime
from typing import Any

from pydantic import BaseModel

from dreamteams.entities.application.entity import ApplicationStatus
from dreamteams.entities.common.identifiers import ApplicationId, CompetitionId, ParticipantId
from dreamteams.entities.common.vo.domain import Domain
from dreamteams.entities.common.vo.participant_type import ParticipantType
from dreamteams.entities.participant.vo.participant_contact import ParticipantContact
from dreamteams.entities.participant.vo.participant_skill import ParticipantSkill
from dreamteams.entities.user import ExperienceLevel


class MyApplicationModel(BaseModel):
    """Participant's view of their own application, including basic competition info."""

    id: ApplicationId
    participant_id: ParticipantId
    competition_id: CompetitionId
    competition_name: str
    domains: list[Domain]
    status: ApplicationStatus
    created_at: datetime
    form_data: dict[str, Any] | None


class ParticipantInfo(BaseModel):
    """Basic participant profile embedded in an organizer-facing application model."""

    id: ParticipantId
    full_name: str
    bio: str | None
    participant_type: ParticipantType
    age: int
    skills: list[ParticipantSkill]
    experience_level: ExperienceLevel | None
    preferred_domains: list[Domain]
    contacts: list[ParticipantContact]


class ApplicationModel(BaseModel):
    """Organizer's view of an application, including competition info and full participant profile."""

    id: ApplicationId
    competition_id: CompetitionId
    competition_name: str
    domains: list[Domain]
    status: ApplicationStatus
    created_at: datetime
    form_data: dict[str, Any] | None
    participant: ParticipantInfo
