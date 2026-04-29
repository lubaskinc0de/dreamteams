"""Shared result models for gateway helpers."""

from dataclasses import dataclass
from datetime import datetime

from dreamteams.application.publish_competition import CreatedCompetition
from dreamteams.application.publish_competition.publish_competition import CompetitionForm
from dreamteams.application.register_user.register_organizer import CreatedOrganizer
from dreamteams.application.register_user.register_participant import CreatedParticipant, ParticipantForm
from dreamteams.entities.common.identifiers import UserId
from dreamteams.presentation.fast_api.routers.organizers import OrganizerForm


@dataclass
class AdminCreated:
    """Credentials for a freshly created admin user."""

    auth_id: str
    user_id: UserId
    created_at: datetime


@dataclass
class OrganizerCreated:
    """Result of registering a new organizer."""

    auth_id: str
    email: str
    form: OrganizerForm
    created: CreatedOrganizer


@dataclass
class ParticipantCreated:
    """Result of registering a new participant."""

    auth_id: str
    email: str
    form: ParticipantForm
    created: CreatedParticipant


@dataclass
class OrganizerWithAdmin:
    """Result of creating an admin and registering an organizer under them."""

    admin: AdminCreated
    organizer: OrganizerCreated


@dataclass
class CompetitionCreated:
    """Result of creating a competition."""

    created: CreatedCompetition
    form: CompetitionForm
