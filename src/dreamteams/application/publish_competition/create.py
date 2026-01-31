import structlog
from pydantic import BaseModel, Field

from dreamteams.application.common.dto.milestone import MilestoneForm
from dreamteams.application.common.idp import IdProvider
from dreamteams.application.common.interactor import interactor
from dreamteams.application.common.logger import Logger
from dreamteams.application.common.uow import UoW
from dreamteams.entities.common.clock import Clock
from dreamteams.entities.common.identifiers import CompetitionId
from dreamteams.entities.common.vo.domain import Domain
from dreamteams.entities.common.vo.participant_type import ParticipantType
from dreamteams.entities.competition.entity import CompetitionData, competition_factory
from dreamteams.entities.competition.milestone import MilestoneData
from dreamteams.entities.competition.participant_limits import ParticipantLimits
from dreamteams.entities.competition.schedule import ScheduleData
from dreamteams.entities.competition.team_size_range import TeamSizeRange
from dreamteams.entities.competition.venue import CompetitionVenue

logger: Logger = structlog.get_logger(__name__)


class CreatedCompetition(BaseModel):
    """Response model containing the created competition identifier."""

    competition_id: CompetitionId


class CompetitionForm(BaseModel):
    """Form for creating a competition."""

    title: str = Field(max_length=200)
    description: str
    schedule: ScheduleData
    participant_limits: ParticipantLimits
    domains: list[Domain]
    participant_type: ParticipantType
    venue: CompetitionVenue
    team_size: TeamSizeRange
    milestones: list[MilestoneForm] = Field(default_factory=list)


@interactor
class CreateCompetition:
    """Interactor for creating a new competition."""

    uow: UoW
    idp: IdProvider
    clock: Clock

    async def execute(self, data: CompetitionForm) -> CreatedCompetition:
        """Creates a new competition."""
        user = await self.idp.get_user()
        logger.debug("Creating competition", title=data.title, user_id=user.id)

        competition = competition_factory(
            CompetitionData(
                title=data.title,
                description=data.description,
                schedule=data.schedule,
                participant_limits=data.participant_limits,
                domains=data.domains,
                participant_type=data.participant_type,
                venue=data.venue,
                team_size=data.team_size,
                milestones=[MilestoneData(milestone.title, milestone.timestamp) for milestone in data.milestones],
            ),
            user,
            self.clock,
        )

        logger.debug(
            "Competition created",
            competition_id=competition.id,
            user_id=user.id,
        )

        self.uow.add(competition)
        await self.uow.commit()

        logger.info("Competition saved", competition_id=competition.id, user_id=user.id)
        return CreatedCompetition(competition_id=competition.id)
