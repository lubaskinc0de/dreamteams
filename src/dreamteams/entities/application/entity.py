from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum, auto
from typing import Any
from uuid import uuid4

from dreamteams.entities.application.form_data_validator import validate_form_data
from dreamteams.entities.application_form.entity import ApplicationForm
from dreamteams.entities.base import Entity, model
from dreamteams.entities.common.clock import Clock
from dreamteams.entities.common.identifiers import ApplicationId, CompetitionId, ParticipantId
from dreamteams.entities.common.vo.domain import Domain
from dreamteams.entities.competition.entity import Competition
from dreamteams.entities.errors.application import ApplicationAlreadyResolvedError, InvalidApplicationDataError
from dreamteams.entities.errors.base import AccessDeniedError
from dreamteams.entities.user import Organizer, Participant


class ApplicationStatus(StrEnum):
    """Status of a registration application."""

    PENDING = auto()
    ACCEPTED = auto()
    REJECTED = auto()


@model
class Application(Entity):
    """Participant's intention to participate in a competition."""

    id: ApplicationId
    participant_id: ParticipantId
    competition_id: CompetitionId
    domains: list[Domain]
    status: ApplicationStatus
    created_at: datetime
    form_data: dict[str, Any] | None = None

    def accept(self, organizer: Organizer, competition: Competition) -> None:
        """Assert organizer access and transition application to ACCEPTED (only from PENDING)."""
        if not competition.is_owned_by(organizer):
            raise AccessDeniedError(message="Only the organizer who owns this competition can accept its applications")
        if self.status != ApplicationStatus.PENDING:
            raise ApplicationAlreadyResolvedError
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

    domains: list[Domain]
    form_data: dict[str, Any] | None = None


def application_factory(
    data: ApplicationData,
    participant: Participant,
    competition: Competition,
    clock: Clock,
    form: ApplicationForm | None = None,
) -> Application:
    """Create a new Application."""
    if not data.domains:
        raise InvalidApplicationDataError(message="Domains list must not be empty")

    if not set(data.domains) <= set(competition.domains):
        raise InvalidApplicationDataError(message="Application domains must be a subset of competition domains")

    validate_form_data(data.form_data, form)

    status = ApplicationStatus.ACCEPTED if competition.auto_accept else ApplicationStatus.PENDING

    return Application(
        id=uuid4(),
        participant_id=participant.id,
        competition_id=competition.id,
        domains=data.domains,
        status=status,
        created_at=clock.now(),
        form_data=data.form_data,
    )
