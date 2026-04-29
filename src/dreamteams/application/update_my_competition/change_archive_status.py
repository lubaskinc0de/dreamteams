import structlog
from pydantic import BaseModel

from dreamteams.application.common.event_bus import EventBus
from dreamteams.application.common.events import CompetitionChanged
from dreamteams.application.common.gateway.competition import CompetitionGateway
from dreamteams.application.common.gateway.organizer import OrganizerGateway
from dreamteams.application.common.idp import IdProvider
from dreamteams.application.errors.organizer import OrganizerNotFoundError
from dreamteams.entities.common.identifiers import CompetitionId
from dreamteams.entities.errors.competition import CompetitionNotFoundError
from dreamteams_common.clock import Clock
from dreamteams_common.interactor import interactor
from dreamteams_common.logger import Logger
from dreamteams_common.uow import UoW

logger: Logger = structlog.get_logger(__name__)


class ChangeCompetitionArchiveStatusForm(BaseModel):
    """Form for changing competition archive status."""

    is_archived: bool


@interactor
class ChangeCompetitionArchiveStatus:
    """Interactor for changing competition archive status."""

    uow: UoW
    idp: IdProvider
    organizer_gateway: OrganizerGateway
    competition_gateway: CompetitionGateway
    event_bus: EventBus
    clock: Clock

    async def execute(self, competition_id: CompetitionId, data: ChangeCompetitionArchiveStatusForm) -> None:
        """Change competition archive status by organizer who created it."""
        user_id = await self.idp.get_user_id()
        logger.debug("Changing competition archive status", competition_id=competition_id, user_id=user_id)

        competition = await self.competition_gateway.get(competition_id)
        if competition is None:
            logger.warning("Competition not found", competition_id=competition_id, user_id=user_id)
            raise CompetitionNotFoundError

        organizer = await self.organizer_gateway.get_by_user_id(user_id)
        if organizer is None:
            raise OrganizerNotFoundError

        competition.change_archive_status(
            is_archived=data.is_archived,
            organizer=organizer,
            clock=self.clock,
        )

        await self.uow.commit()
        await self.event_bus.publish(CompetitionChanged(competition_id=competition_id))

        logger.info("Competition archive status changed", competition_id=competition_id, user_id=user_id)
