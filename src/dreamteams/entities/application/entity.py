from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum, auto
from typing import Any
from uuid import uuid4

from dreamteams.entities.application.form_data_validator import validate_form_data
from dreamteams.entities.application_form.entity import ApplicationForm
from dreamteams.entities.base import Entity
from dreamteams.entities.common.identifiers import ApplicationId, CompetitionId, ParticipantId
from dreamteams.entities.competition.entity import Competition
from dreamteams.entities.competition.track import CompetitionTrack
from dreamteams.entities.errors.application import (
    ApplicationAlreadyResolvedError,
    InvalidApplicationDataError,
    ParticipantLimitsExceededError,
)
from dreamteams.entities.errors.base import AccessDeniedError
from dreamteams.entities.user import Organizer, Participant
from dreamteams_common.clock import Clock


class ApplicationStatus(StrEnum):
    """Status of a registration application."""

    PENDING = auto()
    ACCEPTED = auto()
    REJECTED = auto()


@dataclass
class Application(Entity):
    """Participant's intention to participate in a competition."""

    id: ApplicationId
    participant_id: ParticipantId
    competition_id: CompetitionId
    track: CompetitionTrack
    status: ApplicationStatus
    created_at: datetime
    form_data: dict[str, Any] | None = None

    def ensure_can_accept(self, organizer: Organizer, competition: Competition) -> None:
        """Assert organizer access and that the application is still PENDING."""
        if not competition.is_owned_by(organizer):
            raise AccessDeniedError(message="Only the organizer who owns this competition can accept its applications")
        if self.status != ApplicationStatus.PENDING:
            raise ApplicationAlreadyResolvedError

    def accept(self, organizer: Organizer, competition: Competition, accepted_count: int) -> None:
        """Assert organizer access and transition application to ACCEPTED (only from PENDING)."""
        self.ensure_can_accept(organizer, competition)
        if accepted_count >= competition.participant_limits.max:
            raise ParticipantLimitsExceededError
        self.status = ApplicationStatus.ACCEPTED

    def reject(self, organizer: Organizer, competition: Competition) -> None:
        """Assert organizer access and transition application to REJECTED (only from PENDING)."""
        if not competition.is_owned_by(organizer):
            raise AccessDeniedError(message="Only the organizer who owns this competition can reject its applications")
        if self.status != ApplicationStatus.PENDING:
            raise ApplicationAlreadyResolvedError
        self.status = ApplicationStatus.REJECTED

    def ensure_can_withdraw(self, participant: Participant) -> None:
        """Assert the participant may withdraw this application, raising on any violation."""
        if participant.id != self.participant_id:
            raise AccessDeniedError(message="Only the participant who submitted this application can withdraw it")
        if self.status != ApplicationStatus.PENDING:
            raise ApplicationAlreadyResolvedError


@dataclass(slots=True)
class ApplicationData:
    """Data for creating an Application."""

    track: CompetitionTrack
    form_data: dict[str, Any] | None = None


def application_factory(
    data: ApplicationData,
    participant: Participant,
    competition: Competition,
    clock: Clock,
    form: ApplicationForm | None = None,
) -> Application:
    """Create a new Application."""
    if data.track.name.casefold() not in {track.name.casefold() for track in competition.tracks}:
        raise InvalidApplicationDataError(message="Application track must exist in competition tracks")

    validate_form_data(data.form_data, form)

    status = ApplicationStatus.ACCEPTED if competition.auto_accept else ApplicationStatus.PENDING

    return Application(
        id=uuid4(),
        participant_id=participant.id,
        competition_id=competition.id,
        track=data.track,
        status=status,
        created_at=clock.now(),
        form_data=data.form_data,
    )
