import structlog
from opentelemetry import trace

from dreamteams.application.common.gateway.competition import CompetitionGateway
from dreamteams.application.common.idp import IdProvider
from dreamteams.application.common.interactor import interactor
from dreamteams.application.common.logger import Logger
from dreamteams.application.common.uow import UoW
from dreamteams.entities.common.identifiers import CompetitionId
from dreamteams.entities.errors.base import AccessDeniedError
from dreamteams.entities.errors.competition import CompetitionNotFoundError

logger: Logger = structlog.get_logger(__name__)
_tracer = trace.get_tracer("dreamteams.interactors")


@interactor
class DeleteCompetition:
    """Interactor for deleting a competition."""

    uow: UoW
    idp: IdProvider
    competition_gateway: CompetitionGateway

    async def execute(self, competition_id: CompetitionId) -> None:
        """Deletes competition by organizer who created it."""
        with _tracer.start_as_current_span("interactor.delete_competition"):
            user = await self.idp.get_user()
            logger.debug("Deleting competition", competition_id=competition_id, user_id=user.id)

            competition = await self.competition_gateway.get(competition_id)
            if competition is None:
                logger.warning("Competition not found", competition_id=competition_id, user_id=user.id)
                raise CompetitionNotFoundError

            if not competition.can_delete(user):
                logger.warning(
                    "Attempt to delete competition without permission",
                    competition_id=competition_id,
                    user_id=user.id,
                )
                raise AccessDeniedError(message="Only the organizer who created this competition can delete it")

            await self.uow.delete(competition)
            await self.uow.commit()

            logger.info("Competition deleted", competition_id=competition_id, user_id=user.id)
