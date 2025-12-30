import structlog
from pydantic import BaseModel

from dreamteams.application.common.gateway.competition import CompetitionGateway
from dreamteams.application.common.idp import IdProvider
from dreamteams.application.common.interactor import interactor
from dreamteams.application.common.logger import Logger
from dreamteams.application.common.uow import UoW
from dreamteams.entities.common.identifiers import CompetitionId
from dreamteams.entities.errors.base import AccessDeniedError
from dreamteams.entities.errors.competition import CompetitionNotFoundError

logger: Logger = structlog.get_logger(__name__)


class DeleteCompetitionForm(BaseModel):
    """Form for deleting a competition."""

    competition_id: CompetitionId


@interactor
class DeleteCompetition:
    """Interactor for deleting a competition."""

    uow: UoW
    idp: IdProvider
    competition_gateway: CompetitionGateway

    async def execute(self, data: DeleteCompetitionForm) -> None:
        """Deletes competition by organizer who created it."""
        user = await self.idp.get_user()
        logger.debug("Deleting competition", competition_id=data.competition_id, user_id=user.id)

        competition = await self.competition_gateway.get(data.competition_id)
        if competition is None:
            logger.warning("Competition not found", competition_id=data.competition_id, user_id=user.id)
            raise CompetitionNotFoundError

        if not competition.can_delete(user):
            logger.warning(
                "Attempt to delete competition without permission",
                competition_id=data.competition_id,
                user_id=user.id,
            )
            raise AccessDeniedError

        await self.uow.delete(competition)
        await self.uow.commit()

        logger.info("Competition deleted", competition_id=data.competition_id, user_id=user.id)
