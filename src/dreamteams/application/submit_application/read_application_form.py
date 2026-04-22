import structlog

from dreamteams.application.common.dto.application_form import ApplicationFormModel, to_application_form_model
from dreamteams.application.common.gateway.application_form import ApplicationFormGateway
from dreamteams.application.common.gateway.competition import CompetitionGateway
from dreamteams.application.common.gateway.participant import ParticipantGateway
from dreamteams.application.common.idp import IdProvider
from dreamteams.application.common.interactor import interactor
from dreamteams.application.common.logger import Logger
from dreamteams.application.errors.application_form import ApplicationFormNotFoundError
from dreamteams.entities.common.identifiers import CompetitionId
from dreamteams.entities.errors.base import AccessDeniedError
from dreamteams.entities.errors.competition import CompetitionNotFoundError

logger: Logger = structlog.get_logger(__name__)


@interactor
class ReadApplicationForm:
    """Participant-facing read of a competition's application form."""

    idp: IdProvider
    participant_gateway: ParticipantGateway
    competition_gateway: CompetitionGateway
    application_form_gateway: ApplicationFormGateway

    async def execute(self, competition_id: CompetitionId) -> ApplicationFormModel:
        """Read the application form attached to a competition as a participant."""
        user_id = await self.idp.get_user_id()
        logger.debug("Participant reading application form", competition_id=competition_id, user_id=user_id)

        participant = await self.participant_gateway.get_by_user_id(user_id)
        if participant is None:
            logger.warning("User has no participant profile", user_id=user_id)
            raise AccessDeniedError(message="Only participants can read application forms")

        competition = await self.competition_gateway.get(competition_id)
        if competition is None:
            logger.warning("Competition not found", competition_id=competition_id, user_id=user_id)
            raise CompetitionNotFoundError

        form = await self.application_form_gateway.get_by_competition_id(competition_id)
        if form is None:
            logger.warning("Application form not found", competition_id=competition_id, user_id=user_id)
            raise ApplicationFormNotFoundError

        return to_application_form_model(form)
