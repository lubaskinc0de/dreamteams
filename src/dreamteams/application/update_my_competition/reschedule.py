import structlog
from pydantic import BaseModel

from dreamteams.application.common.competition_cache import CompetitionCache
from dreamteams.application.common.gateway.competition import CompetitionGateway
from dreamteams.application.common.gateway.organizer import OrganizerGateway
from dreamteams.application.common.idp import IdProvider
from dreamteams.application.errors.organizer import OrganizerNotFoundError
from dreamteams.entities.common.identifiers import CompetitionId
from dreamteams.entities.competition.schedule import ScheduleData
from dreamteams.entities.competition.team_size_range import TeamSizeRange
from dreamteams.entities.errors.competition import CompetitionNotFoundError
from dreamteams_common.clock import Clock
from dreamteams_common.interactor import interactor
from dreamteams_common.logger import Logger
from dreamteams_common.uow import UoW

logger: Logger = structlog.get_logger(__name__)


class RescheduleCompetitionForm(BaseModel):
    """Form for rescheduling a competition."""

    schedule: ScheduleData
    team_size: TeamSizeRange | None


@interactor
class RescheduleCompetition:
    """Interactor for updating competition schedule."""

    uow: UoW
    idp: IdProvider
    organizer_gateway: OrganizerGateway
    competition_gateway: CompetitionGateway
    competition_cache: CompetitionCache
    clock: Clock

    async def execute(self, competition_id: CompetitionId, data: RescheduleCompetitionForm) -> None:
        """Reschedule competition by organizer who created it."""
        user_id = await self.idp.get_user_id()
        logger.debug("Rescheduling competition", competition_id=competition_id, user_id=user_id)

        competition = await self.competition_gateway.get(competition_id)
        if competition is None:
            logger.warning("Competition not found", competition_id=competition_id, user_id=user_id)
            raise CompetitionNotFoundError

        organizer = await self.organizer_gateway.get_by_user_id(user_id)
        if organizer is None:
            raise OrganizerNotFoundError

        competition.reschedule(
            schedule=data.schedule,
            team_size=data.team_size,
            organizer=organizer,
            clock=self.clock,
        )

        await self.uow.commit()
        await self.competition_cache.delete_read(competition_id)
        await self.competition_cache.clear_preview()

        logger.info("Competition rescheduled", competition_id=competition_id, user_id=user_id)
