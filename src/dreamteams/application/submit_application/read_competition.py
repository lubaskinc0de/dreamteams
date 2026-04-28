import structlog

from dreamteams.application.common.dto.competition import CompetitionModel
from dreamteams.application.common.gateway.competition import CompetitionGateway
from dreamteams.application.common.gateway.participant import ParticipantGateway
from dreamteams.application.common.idp import IdProvider
from dreamteams.entities.common.identifiers import CompetitionId
from dreamteams.entities.errors.base import AccessDeniedError
from dreamteams.entities.errors.competition import CompetitionNotFoundError
from dreamteams_common.interactor import interactor
from dreamteams_common.logger import Logger

logger: Logger = structlog.get_logger(__name__)


@interactor
class ReadCompetition:
    """Participant-facing read of a single competition by ID."""

    idp: IdProvider
    participant_gateway: ParticipantGateway
    competition_gateway: CompetitionGateway

    async def execute(self, competition_id: CompetitionId) -> CompetitionModel:
        """Read a competition by ID as a participant."""
        user_id = await self.idp.get_user_id()
        logger.debug("Participant reading competition", competition_id=competition_id, user_id=user_id)

        participant = await self.participant_gateway.get_by_user_id(user_id)
        if participant is None:
            logger.warning("User has no participant profile", user_id=user_id)
            raise AccessDeniedError(message="Only participants can read competitions")

        model = await self.competition_gateway.read(competition_id)
        if model is None:
            logger.warning("Competition not found", competition_id=competition_id, user_id=user_id)
            raise CompetitionNotFoundError

        return model
