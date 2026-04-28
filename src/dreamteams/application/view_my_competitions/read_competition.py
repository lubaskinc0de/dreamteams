import structlog

from dreamteams.application.common.dto.competition import CompetitionModel
from dreamteams.application.common.gateway.competition import CompetitionGateway
from dreamteams.application.common.gateway.organizer import OrganizerGateway
from dreamteams.application.common.idp import IdProvider
from dreamteams.application.common.interactor import interactor
from dreamteams.application.common.logger import Logger
from dreamteams.application.errors.organizer import OrganizerNotFoundError
from dreamteams.entities.common.identifiers import CompetitionId
from dreamteams.entities.errors.base import AccessDeniedError
from dreamteams.entities.errors.competition import CompetitionNotFoundError

logger: Logger = structlog.get_logger(__name__)


@interactor
class ReadCompetition:
    """Interactor for reading competition by ID."""

    idp: IdProvider
    organizer_gateway: OrganizerGateway
    competition_gateway: CompetitionGateway

    async def execute(self, competition_id: CompetitionId) -> CompetitionModel:
        """Read competition by ID (members_count included)."""
        user_id = await self.idp.get_user_id()
        logger.debug("Reading competition", competition_id=competition_id, user_id=user_id)

        model = await self.competition_gateway.read(competition_id)
        if model is None:
            logger.warning("Competition not found", competition_id=competition_id, user_id=user_id)
            raise CompetitionNotFoundError

        organizer = await self.organizer_gateway.get_by_user_id(user_id)
        if organizer is None:
            raise OrganizerNotFoundError
        if model.organizer_id != organizer.id:
            logger.warning("Access denied to read competition", competition_id=competition_id, user_id=user_id)
            raise AccessDeniedError(message="Only the organizer who created this competition can view it")

        return model
