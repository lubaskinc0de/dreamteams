import structlog

from dreamteams.application.common.dto.application_form import (
    ApplicationFormModel,
    FieldChoiceModel,
    FieldModel,
    to_application_form_model,
)
from dreamteams.application.common.gateway.application_form import ApplicationFormGateway
from dreamteams.application.common.gateway.competition import CompetitionGateway
from dreamteams.application.common.gateway.organizer import OrganizerGateway
from dreamteams.application.common.idp import IdProvider
from dreamteams.application.errors.application_form import ApplicationFormNotFoundError
from dreamteams.application.errors.organizer import OrganizerNotFoundError
from dreamteams.entities.common.identifiers import CompetitionId
from dreamteams.entities.errors.base import AccessDeniedError
from dreamteams.entities.errors.competition import CompetitionNotFoundError
from dreamteams_common.interactor import interactor
from dreamteams_common.logger import Logger

logger: Logger = structlog.get_logger(__name__)

__all__ = [
    "ApplicationFormModel",
    "FieldChoiceModel",
    "FieldModel",
    "ReadApplicationForm",
]


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

        return to_application_form_model(form)
