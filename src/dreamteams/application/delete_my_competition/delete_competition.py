import structlog

from dreamteams.application.common.competition_cache import CompetitionCache
from dreamteams.application.common.gateway.competition import CompetitionGateway
from dreamteams.application.common.gateway.organizer import OrganizerGateway
from dreamteams.application.common.idp import IdProvider
from dreamteams.application.common.interactor import interactor
from dreamteams.application.common.logger import Logger
from dreamteams.application.common.uow import UoW
from dreamteams.application.errors.organizer import OrganizerNotFoundError
from dreamteams.entities.common.identifiers import CompetitionId
from dreamteams.entities.errors.base import AccessDeniedError
from dreamteams.entities.errors.competition import CompetitionNotFoundError

logger: Logger = structlog.get_logger(__name__)


@interactor
class DeleteCompetition:
    """Interactor for deleting a competition."""

    uow: UoW
    idp: IdProvider
    organizer_gateway: OrganizerGateway
    competition_gateway: CompetitionGateway
    competition_cache: CompetitionCache

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
        await self.competition_cache.delete_read(competition_id)
        await self.competition_cache.clear_preview()

        logger.info("Competition deleted", competition_id=competition_id, user_id=user_id)
