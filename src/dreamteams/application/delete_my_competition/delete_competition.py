import structlog

from dreamteams.application.common.event_bus import EventBus
from dreamteams.application.common.events import CompetitionDeleted
from dreamteams.application.common.gateway.competition import CompetitionGateway
from dreamteams.application.common.gateway.organizer import OrganizerGateway
from dreamteams.application.common.idp import IdProvider
from dreamteams.application.errors.organizer import OrganizerNotFoundError
from dreamteams.entities.common.identifiers import CompetitionId
from dreamteams.entities.errors.base import AccessDeniedError
from dreamteams.entities.errors.competition import CompetitionNotFoundError
from dreamteams_common.interactor import interactor
from dreamteams_common.logger import Logger
from dreamteams_common.uow import UoW

logger: Logger = structlog.get_logger(__name__)


@interactor
class DeleteCompetition:
    """Interactor for deleting a competition."""

    uow: UoW
    idp: IdProvider
    organizer_gateway: OrganizerGateway
    competition_gateway: CompetitionGateway
    event_bus: EventBus

    async def execute(self, competition_id: CompetitionId) -> None:
        """Deletes competition by organizer who created it."""
        user_id = await self.idp.get_user_id()
        logger.debug("Deleting competition", competition_id=competition_id, user_id=user_id)

        competition = await self.competition_gateway.get(competition_id)
        if competition is None:
            logger.warning("Competition not found", competition_id=competition_id, user_id=user_id)
            raise CompetitionNotFoundError

        organizer = await self.organizer_gateway.get_by_user_id(user_id)
        if organizer is None:
            raise OrganizerNotFoundError
        if not competition.is_owned_by(organizer):
            logger.warning(
                "Attempt to delete competition without permission",
                competition_id=competition_id,
                user_id=user_id,
            )
            raise AccessDeniedError(message="Only the organizer who created this competition can delete it")

        await self.uow.delete(competition)
        await self.uow.commit()
        await self.event_bus.publish(CompetitionDeleted(competition_id=competition_id))

        logger.info("Competition deleted", competition_id=competition_id, user_id=user_id)
