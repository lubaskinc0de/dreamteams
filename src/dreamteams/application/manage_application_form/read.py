from datetime import datetime

import structlog
from pydantic import BaseModel

from dreamteams.application.common.gateway.application_form import ApplicationFormGateway
from dreamteams.application.common.gateway.competition import CompetitionGateway
from dreamteams.application.common.gateway.organizer import OrganizerGateway
from dreamteams.application.common.idp import IdProvider
from dreamteams.application.common.interactor import interactor
from dreamteams.application.common.logger import Logger
from dreamteams.application.errors.application_form import ApplicationFormNotFoundError
from dreamteams.application.errors.organizer import OrganizerNotFoundError
from dreamteams.entities.application_form.vo.field import FieldType
from dreamteams.entities.common.identifiers import ApplicationFormId, CompetitionId
from dreamteams.entities.errors.base import AccessDeniedError
from dreamteams.entities.errors.competition import CompetitionNotFoundError

logger: Logger = structlog.get_logger(__name__)


class FieldChoiceModel(BaseModel):
    """A single selectable option in a SELECT or MULTISELECT field."""

    value: str
    label: str


class FieldModel(BaseModel):
    """A single field definition in an application form."""

    name: str
    label: str
    type: FieldType
    required: bool
    choices: list[FieldChoiceModel] | None


class ApplicationFormModel(BaseModel):
    """Full representation of an application form."""

    id: ApplicationFormId
    competition_id: CompetitionId
    created_at: datetime
    fields: list[FieldModel]


@interactor
class ReadApplicationForm:
    """Interactor for reading the application form of a competition."""

    idp: IdProvider
    organizer_gateway: OrganizerGateway
    competition_gateway: CompetitionGateway
    application_form_gateway: ApplicationFormGateway

    async def execute(self, competition_id: CompetitionId) -> ApplicationFormModel:
        """Read the application form for a competition."""
        user_id = await self.idp.get_user_id()
        logger.debug("Reading application form", competition_id=competition_id, user_id=user_id)

        competition = await self.competition_gateway.get(competition_id)
        if competition is None:
            logger.warning("Competition not found", competition_id=competition_id, user_id=user_id)
            raise CompetitionNotFoundError

        organizer = await self.organizer_gateway.get_by_user_id(user_id)
        if organizer is None:
            raise OrganizerNotFoundError
        if not competition.is_owned_by(organizer):
            logger.warning("Access denied to read application form", competition_id=competition_id, user_id=user_id)
            raise AccessDeniedError(message="Only the organizer who created this competition can view its form")

        form = await self.application_form_gateway.get_by_competition_id(competition_id)
        if form is None:
            logger.warning("Application form not found", competition_id=competition_id, user_id=user_id)
            raise ApplicationFormNotFoundError

        return ApplicationFormModel(
            id=form.id,
            competition_id=form.competition_id,
            created_at=form.created_at,
            fields=[
                FieldModel(
                    name=f.name,
                    label=f.label,
                    type=f.type,
                    required=f.required,
                    choices=(
                        [FieldChoiceModel(value=c.value, label=c.label) for c in f.choices]
                        if f.choices is not None
                        else None
                    ),
                )
                for f in form.fields
            ],
        )
