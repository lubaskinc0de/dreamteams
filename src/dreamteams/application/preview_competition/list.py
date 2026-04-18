from datetime import datetime

import structlog
from pydantic import BaseModel, Field

from dreamteams.application.common.avatar_storage import AvatarStorage
from dreamteams.application.common.gateway.competition import CompetitionGateway, CompetitionSortBy
from dreamteams.application.common.gateway.sorting import SortOrder
from dreamteams.application.common.interactor import interactor
from dreamteams.application.common.logger import Logger
from dreamteams.entities.common.identifiers import CompetitionId, OrganizerId
from dreamteams.entities.common.vo.domain import Domain
from dreamteams.entities.common.vo.participant_type import ParticipantType
from dreamteams.entities.competition.milestone import Milestone
from dreamteams.entities.competition.participant_limits import ParticipantLimits
from dreamteams.entities.competition.schedule import CompetitionSchedule
from dreamteams.entities.competition.team_size_range import TeamSizeRange
from dreamteams.entities.competition.venue import CompetitionVenue

PAGE_SIZE = 10
logger: Logger = structlog.get_logger(__name__)


class PreviewCompetitionsInput(BaseModel):
    """Input parameters for listing preview competitions."""

    page: int = Field(ge=1, default=1)


class PreviewOrganizerModel(BaseModel):
    """Response model containing organizer preview information."""

    id: OrganizerId
    name: str
    avatar_url: str | None


class PreviewCompetitionModel(BaseModel):
    """Response model containing competition data with organizer info for preview."""

    id: CompetitionId
    organizer: PreviewOrganizerModel
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


class PreviewCompetitionsList(BaseModel):
    """Response model containing paginated list of preview competitions."""

    items: list[PreviewCompetitionModel]
    total: int
    page: int


@interactor
class PreviewCompetitions:
    """Interactor for listing preview competitions."""

    competition_gateway: CompetitionGateway
    avatar_storage: AvatarStorage

    async def execute(self, input_data: PreviewCompetitionsInput) -> PreviewCompetitionsList:
        """Interactor for viewing competitions as anonymous user."""
        logger.info("Preview competitions called", page_size=PAGE_SIZE, page=input_data.page)
        competitions, total = await self.competition_gateway.list(
            organizer_id=None,
            page=input_data.page,
            page_size=PAGE_SIZE,
            sort_by=CompetitionSortBy.CREATED_AT,
            sort_order=SortOrder.DESC,
            is_archived=False,
            search=None,
            active=True,
            eager_organizer=True,
            eager_milestones=True,
        )

        items = [
            PreviewCompetitionModel(
                id=competition.id,
                organizer=PreviewOrganizerModel(
                    id=competition.organizer.id,
                    name=competition.organizer.organizer_name,
                    avatar_url=(
                        self.avatar_storage.get_url(competition.organizer.user.avatar)
                        if competition.organizer.user.avatar is not None
                        else None
                    ),
                ),
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
            for competition in competitions
        ]

        return PreviewCompetitionsList(items=items, total=total, page=input_data.page)
