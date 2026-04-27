import structlog

from dreamteams.application.common.dto.application import MyApplicationModel
from dreamteams.application.common.gateway.application import ApplicationGateway
from dreamteams.application.common.gateway.competition import CompetitionGateway
from dreamteams.application.common.gateway.participant import ParticipantGateway
from dreamteams.application.common.idp import IdProvider
from dreamteams.application.common.interactor import interactor
from dreamteams.application.common.logger import Logger
from dreamteams.application.errors.application import ApplicationNotFoundError
from dreamteams.entities.common.identifiers import ApplicationId
from dreamteams.entities.errors.base import AccessDeniedError
from dreamteams.entities.errors.competition import CompetitionNotFoundError

logger: Logger = structlog.get_logger(__name__)


@interactor
class ReadMyApplication:
    """Interactor for reading a single application owned by the current participant."""

    idp: IdProvider
    participant_gateway: ParticipantGateway
    application_gateway: ApplicationGateway
    competition_gateway: CompetitionGateway

    async def execute(self, application_id: ApplicationId) -> MyApplicationModel:
        """Read a single application; only the submitting participant may access it."""
        user_id = await self.idp.get_user_id()
        logger.debug("Reading own application", application_id=application_id, user_id=user_id)

        application = await self.application_gateway.get(application_id)
        if application is None:
            logger.warning("Application not found", application_id=application_id, user_id=user_id)
            raise ApplicationNotFoundError

        participant = await self.participant_gateway.get_by_user_id(user_id)
        if participant is None or participant.id != application.participant_id:
            logger.warning("Access denied to read application", application_id=application_id, user_id=user_id)
            raise AccessDeniedError(message="Only the participant who submitted this application can read it")

        competition = await self.competition_gateway.get(application.competition_id)
        if competition is None:
            raise CompetitionNotFoundError

        return MyApplicationModel(
            id=application.id,
            participant_id=application.participant_id,
            competition_id=application.competition_id,
            competition_name=competition.title,
            track=application.track,
            status=application.status,
            created_at=application.created_at,
            form_data=application.form_data,
        )
