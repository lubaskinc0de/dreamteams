from datetime import datetime

import structlog
from pydantic import BaseModel

from dreamteams.application.common.gateway.competition import CompetitionGateway
from dreamteams.application.common.gateway.organizer import OrganizerGateway
from dreamteams.application.common.idp import IdProvider
from dreamteams.application.common.interactor import interactor
from dreamteams.application.common.logger import Logger
from dreamteams.application.errors.organizer import OrganizerNotFoundError
from dreamteams.entities.common.identifiers import CompetitionId, OrganizerId
from dreamteams.entities.common.vo.domain import Domain
from dreamteams.entities.common.vo.participant_type import ParticipantType
from dreamteams.entities.competition.milestone import Milestone
from dreamteams.entities.competition.participant_limits import ParticipantLimits
from dreamteams.entities.competition.schedule import CompetitionSchedule
from dreamteams.entities.competition.team_size_range import TeamSizeRange
from dreamteams.entities.competition.venue import CompetitionVenue
from dreamteams.entities.errors.base import AccessDeniedError
from dreamteams.entities.errors.competition import CompetitionNotFoundError

logger: Logger = structlog.get_logger(__name__)


class CompetitionModel(BaseModel):
    """Response model containing competition data."""

    id: CompetitionId
    organizer_id: OrganizerId
    title: str
    banner: str | None
    description: str
    schedule: CompetitionSchedule
    participant_limits: ParticipantLimits
    domains: list[Domain]
    participant_type: ParticipantType
    venue: CompetitionVenue
    team_size: TeamSizeRange
    milestones: list[Milestone]
    auto_accept: bool
    is_archived: bool
    created_at: datetime
    updated_at: datetime


@interactor
class ReadCompetition:
    """Interactor for reading competition by ID."""

    idp: IdProvider
    organizer_gateway: OrganizerGateway
    competition_gateway: CompetitionGateway

    async def execute(self, competition_id: CompetitionId) -> CompetitionModel:
        """Read competition by ID."""
        user_id = await self.idp.get_user_id()
        logger.debug("Reading competition", competition_id=competition_id, user_id=user_id)

        competition = await self.competition_gateway.get(competition_id, eager_milestones=True)
        if competition is None:
            logger.warning("Competition not found", competition_id=competition_id, user_id=user_id)
            raise CompetitionNotFoundError

        organizer = await self.organizer_gateway.get_by_user_id(user_id)
        if organizer is None:
            raise OrganizerNotFoundError
        if not competition.is_owned_by(organizer):
            logger.warning("Access denied to read competition", competition_id=competition_id, user_id=user_id)
            raise AccessDeniedError(message="Only the organizer who created this competition can view it")

        return CompetitionModel(
            id=competition.id,
            organizer_id=competition.organizer_id,
            title=competition.title,
            banner=competition.banner,
            description=competition.description,
            schedule=competition.schedule,
            participant_limits=competition.participant_limits,
            domains=competition.domains,
            participant_type=competition.participant_type,
            venue=competition.venue,
            team_size=competition.team_size,
            milestones=competition.milestones,
            auto_accept=competition.auto_accept,
            is_archived=competition.is_archived,
            created_at=competition.created_at,
            updated_at=competition.updated_at,
        )
