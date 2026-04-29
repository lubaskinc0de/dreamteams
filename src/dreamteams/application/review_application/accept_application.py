import structlog

from dreamteams.application.common.event_bus import EventBus
from dreamteams.application.common.events import ApplicationAccepted
from dreamteams.application.common.gateway.application import ApplicationGateway
from dreamteams.application.common.gateway.competition import CompetitionGateway
from dreamteams.application.common.gateway.organizer import OrganizerGateway
from dreamteams.application.common.idp import IdProvider
from dreamteams.application.errors.application import ApplicationNotFoundError
from dreamteams.application.errors.organizer import OrganizerNotFoundError
from dreamteams.entities.common.identifiers import ApplicationId
from dreamteams.entities.errors.competition import CompetitionNotFoundError
from dreamteams_common.interactor import interactor
from dreamteams_common.logger import Logger
from dreamteams_common.uow import UoW

logger: Logger = structlog.get_logger(__name__)


@interactor
class AcceptApplication:
    """Interactor for accepting a pending application (PENDING → ACCEPTED)."""

    uow: UoW
    idp: IdProvider
    organizer_gateway: OrganizerGateway
    application_gateway: ApplicationGateway
    competition_gateway: CompetitionGateway
    event_bus: EventBus

    async def execute(self, application_id: ApplicationId) -> None:
        """Accept a pending application; delegates access and status checks to the domain."""
        user_id = await self.idp.get_user_id()
        logger.debug("Accepting application", application_id=application_id, user_id=user_id)

        application = await self.application_gateway.get(application_id)
        if application is None:
            logger.warning("Application not found", application_id=application_id, user_id=user_id)
            raise ApplicationNotFoundError

        competition = await self.competition_gateway.get(application.competition_id, for_update=True)
        if competition is None:
            raise CompetitionNotFoundError

        organizer = await self.organizer_gateway.get_by_user_id(user_id)
        if organizer is None:
            raise OrganizerNotFoundError

        accepted_count = await self.application_gateway.count_accepted_by_competition(application.competition_id)
        application.accept(organizer, competition, accepted_count)

        self.uow.add(application)
        await self.uow.commit()
        await self.event_bus.publish(
            ApplicationAccepted(application_id=application.id, competition_id=application.competition_id),
        )

        logger.info("Application accepted", application_id=application_id, user_id=user_id)
