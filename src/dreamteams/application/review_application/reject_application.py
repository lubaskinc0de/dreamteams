import structlog

from dreamteams.application.common.competition_cache import CompetitionCache
from dreamteams.application.common.gateway.application import ApplicationGateway
from dreamteams.application.common.gateway.competition import CompetitionGateway
from dreamteams.application.common.gateway.organizer import OrganizerGateway
from dreamteams.application.common.idp import IdProvider
from dreamteams.application.common.interactor import interactor
from dreamteams.application.common.logger import Logger
from dreamteams.application.common.metrics import MetricsGateway
from dreamteams.application.common.uow import UoW
from dreamteams.application.errors.application import ApplicationNotFoundError
from dreamteams.application.errors.organizer import OrganizerNotFoundError
from dreamteams.entities.common.identifiers import ApplicationId
from dreamteams.entities.errors.competition import CompetitionNotFoundError

logger: Logger = structlog.get_logger(__name__)


@interactor
class RejectApplication:
    """Interactor for rejecting a pending application (PENDING → REJECTED)."""

    uow: UoW
    idp: IdProvider
    organizer_gateway: OrganizerGateway
    application_gateway: ApplicationGateway
    competition_gateway: CompetitionGateway
    competition_cache: CompetitionCache
    metrics: MetricsGateway

    async def execute(self, application_id: ApplicationId) -> None:
        """Reject a pending application; delegates access and status checks to the domain."""
        user_id = await self.idp.get_user_id()
        logger.debug("Rejecting application", application_id=application_id, user_id=user_id)

        application = await self.application_gateway.get(application_id)
        if application is None:
            logger.warning("Application not found", application_id=application_id, user_id=user_id)
            raise ApplicationNotFoundError

        competition = await self.competition_gateway.get(application.competition_id)
        if competition is None:
            raise CompetitionNotFoundError

        organizer = await self.organizer_gateway.get_by_user_id(user_id)
        if organizer is None:
            raise OrganizerNotFoundError

        application.reject(organizer, competition)

        self.uow.add(application)
        await self.uow.commit()
        await self.competition_cache.delete_read(application.competition_id)
        await self.competition_cache.clear_preview()

        self.metrics.record_application_rejected()
        logger.info("Application rejected", application_id=application_id, user_id=user_id)
