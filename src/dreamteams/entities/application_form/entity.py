from dataclasses import dataclass
from datetime import datetime
from uuid import uuid4

from dreamteams.entities.application_form.vo.fields import ApplicationFormFields
from dreamteams.entities.base import Entity
from dreamteams.entities.common.identifiers import ApplicationFormId, CompetitionId
from dreamteams.entities.competition.entity import Competition
from dreamteams.entities.errors.base import AccessDeniedError
from dreamteams.entities.user import Organizer
from dreamteams_common.clock import Clock


@dataclass
class ApplicationForm(Entity):
    """An optional set of extra fields an organizer attaches to a competition."""

    id: ApplicationFormId
    competition_id: CompetitionId
    created_at: datetime
    fields: ApplicationFormFields


@dataclass(slots=True)
class ApplicationFormData:
    """Input data for creating an ApplicationForm."""

    fields: ApplicationFormFields


def application_form_factory(
    data: ApplicationFormData,
    competition: Competition,
    organizer: Organizer,
    clock: Clock,
) -> ApplicationForm:
    """Create a new ApplicationForm for a competition."""
    if organizer.id != competition.organizer_id:
        raise AccessDeniedError(message="Only the competition owner can create an application form")

    return ApplicationForm(
        id=uuid4(),
        competition_id=competition.id,
        created_at=clock.now(),
        fields=ApplicationFormFields(data.fields),
    )
