import structlog
from pydantic import BaseModel, Field

from dreamteams.application.common.gateway.competition import CompetitionGateway, CompetitionSortBy
from dreamteams.application.common.gateway.sorting import SortOrder
from dreamteams.application.common.idp import IdProvider
from dreamteams.application.common.interactor import interactor
from dreamteams.application.common.logger import Logger
from dreamteams.application.manage_competitions.read import CompetitionModel
from dreamteams.entities.errors.base import AccessDeniedError

logger: Logger = structlog.get_logger(__name__)

PAGE_SIZE = 10


class ListCompetitionsInput(BaseModel):
    """Input parameters for listing competitions."""

    page: int = Field(ge=1, default=1)
    sort_by: CompetitionSortBy = CompetitionSortBy.CREATED_AT
    sort_order: SortOrder = SortOrder.DESC
    is_archived: bool | None = None
    search: str | None = None


class CompetitionsList(BaseModel):
    """Response model containing paginated list of competitions."""

    items: list[CompetitionModel]
    total: int
    page: int


@interactor
class ListCompetitions:
    """Interactor for listing competitions by organizer."""

    idp: IdProvider
    competition_gateway: CompetitionGateway

    async def execute(self, input_data: ListCompetitionsInput) -> CompetitionsList:
        """List competitions for current organizer."""
        user = await self.idp.get_user()
        if user.organizer is None:
            logger.warning("User has no organizer role", user_id=user.id)
            raise AccessDeniedError(message="Only organizers can list competitions")

        logger.debug(
            "Listing competitions",
            user_id=user.id,
            page=input_data.page,
            sort_by=input_data.sort_by,
            sort_order=input_data.sort_order,
            is_archived=input_data.is_archived,
            search=input_data.search,
            page_size=PAGE_SIZE,
            organizer_id=user.organizer.id,
        )
        competitions, total = await self.competition_gateway.list(
            user.organizer.id,
            page=input_data.page,
            page_size=PAGE_SIZE,
            sort_by=input_data.sort_by,
            sort_order=input_data.sort_order,
            is_archived=input_data.is_archived,
            search=input_data.search,
            active=None,
        )

        items = [
            CompetitionModel(
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
            for competition in competitions
        ]

        return CompetitionsList(items=items, total=total, page=input_data.page)
