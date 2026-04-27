import structlog
from pydantic import BaseModel, Field

from dreamteams.application.common.dto.milestone import MilestoneForm
from dreamteams.application.common.gateway.competition import CompetitionGateway
from dreamteams.application.common.gateway.organizer import OrganizerGateway
from dreamteams.application.common.idp import IdProvider
from dreamteams.application.common.interactor import interactor
from dreamteams.application.common.logger import Logger
from dreamteams.application.common.uow import UoW
from dreamteams.application.errors.organizer import OrganizerNotFoundError
from dreamteams.entities.common.clock import Clock
from dreamteams.entities.common.identifiers import CompetitionId
from dreamteams.entities.common.vo.domain import Domain
from dreamteams.entities.common.vo.participant_type import ParticipantType
from dreamteams.entities.competition.entity import UpdateCompetitionData
from dreamteams.entities.competition.milestone import MilestoneData, milestone_factory
from dreamteams.entities.competition.participant_limits import ParticipantLimits
from dreamteams.entities.competition.schedule import ScheduleData
from dreamteams.entities.competition.team_size_range import TeamSizeRange
from dreamteams.entities.competition.venue import CompetitionVenue
from dreamteams.entities.competition.vo.milestones import CompetitionMilestones
from dreamteams.entities.errors.competition import CompetitionNotFoundError

logger: Logger = structlog.get_logger(__name__)


class UpdateCompetitionForm(BaseModel):
    """Form for updating a competition."""

    title: str = Field(max_length=200)
    description: str = Field(min_length=1)
    schedule: ScheduleData
    participant_limits: ParticipantLimits
    domains: list[Domain]
    participant_type: ParticipantType
    venue: CompetitionVenue
    team_size: TeamSizeRange | None
    milestones: list[MilestoneForm] | None
    auto_accept: bool
    is_archived: bool


@interactor
class UpdateCompetition:
    """Interactor for updating a competition."""

    uow: UoW
    idp: IdProvider
    organizer_gateway: OrganizerGateway
    competition_gateway: CompetitionGateway
    clock: Clock

    async def execute(self, competition_id: CompetitionId, data: UpdateCompetitionForm) -> None:
        """Updates competition by organizer who created it."""
        user_id = await self.idp.get_user_id()
        logger.debug("Updating competition", competition_id=competition_id, user_id=user_id)

        competition = await self.competition_gateway.get(competition_id, eager_milestones=True)
        if competition is None:
            logger.warning("Competition not found", competition_id=competition_id, user_id=user_id)
            raise CompetitionNotFoundError

        organizer = await self.organizer_gateway.get_by_user_id(user_id)
        if organizer is None:
            raise OrganizerNotFoundError

        if data.milestones is not None:
            await self.competition_gateway.clear_milestones(competition_id)

        competition.update(
            organizer=organizer,
            clock=self.clock,
            data=UpdateCompetitionData(
                title=data.title,
                description=data.description,
                schedule=data.schedule,
                participant_limits=data.participant_limits,
                domains=data.domains,
                participant_type=data.participant_type,
                venue=data.venue,
                team_size=data.team_size,
                milestones=CompetitionMilestones(
                    [
                        milestone_factory(
                            MilestoneData(
                                title=milestone.title,
                                timestamp=milestone.timestamp,
                                description=milestone.description,
                            ),
                            self.clock,
                        )
                        for milestone in data.milestones
                    ],
                )
                if data.milestones is not None
                else None,
                auto_accept=data.auto_accept,
                is_archived=data.is_archived,
            ),
        )

        await self.uow.commit()

        logger.info("Competition updated", competition_id=competition_id, user_id=user_id)
