import structlog

from dreamteams.application.common.gateway.application import ApplicationGateway
from dreamteams.application.common.gateway.competition import CompetitionGateway
from dreamteams.application.common.idp import IdProvider
from dreamteams.application.common.interactor import interactor
from dreamteams.application.common.logger import Logger
from dreamteams.application.errors.application import ApplicationNotFoundError
from dreamteams.application.manage_my_applications.read import ApplicationModel
from dreamteams.entities.common.identifiers import ApplicationId
from dreamteams.entities.errors.base import AccessDeniedError

logger: Logger = structlog.get_logger(__name__)


@interactor
class ReadApplication:
    """Interactor for reading a single application (organizer access)."""

    idp: IdProvider
    application_gateway: ApplicationGateway
    competition_gateway: CompetitionGateway

    async def execute(self, application_id: ApplicationId) -> ApplicationModel:
        """Read a single application; only the organizer who owns the competition may access it."""
        user = await self.idp.get_user()
        logger.debug("Reading application", application_id=application_id, user_id=user.id)

        application = await self.application_gateway.get(application_id)
        if application is None:
            logger.warning("Application not found", application_id=application_id, user_id=user.id)
            raise ApplicationNotFoundError

        competition = await self.competition_gateway.get(application.competition_id)
        if competition is None or not competition.can_read(user):
            logger.warning("Access denied to read application", application_id=application_id, user_id=user.id)
            raise AccessDeniedError(message="Only the organizer who owns this competition can read its applications")

        return ApplicationModel(
            id=application.id,
            participant_id=application.participant_id,
            competition_id=application.competition_id,
            domains=application.domains,
            status=application.status,
            created_at=application.created_at,
            form_data=application.form_data,
        )
