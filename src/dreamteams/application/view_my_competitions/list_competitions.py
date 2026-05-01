import structlog
from pydantic import BaseModel, Field

from dreamteams.application.common.dto.competition import CompetitionModel
from dreamteams.application.common.gateway.competition import CompetitionGateway, CompetitionSortBy
from dreamteams.application.common.gateway.organizer import OrganizerGateway
from dreamteams.application.common.gateway.sorting import SortOrder
from dreamteams.application.common.idp import IdProvider
from dreamteams.application.common.input_limits import MAX_PAGE, MAX_SEARCH_LENGTH
from dreamteams.entities.errors.base import AccessDeniedError
from dreamteams_common.interactor import interactor
from dreamteams_common.logger import Logger

logger: Logger = structlog.get_logger(__name__)
PAGE_SIZE = 10


class ListCompetitionsInput(BaseModel):
    """Input parameters for listing competitions."""

    page: int = Field(ge=1, le=MAX_PAGE, default=1)
    sort_by: CompetitionSortBy = CompetitionSortBy.CREATED_AT
    sort_order: SortOrder = SortOrder.DESC
    is_archived: bool | None = None
    search: str | None = Field(default=None, max_length=MAX_SEARCH_LENGTH)


class CompetitionsList(BaseModel):
    """Response model containing paginated list of competitions."""

    items: list[CompetitionModel]
    total: int
    page: int


@interactor
class ListCompetitions:
    """Interactor for listing competitions by organizer."""

    idp: IdProvider
    organizer_gateway: OrganizerGateway
    competition_gateway: CompetitionGateway

    async def execute(self, input_data: ListCompetitionsInput) -> CompetitionsList:
        """List competitions for current organizer."""
        user_id = await self.idp.get_user_id()
        organizer = await self.organizer_gateway.get_by_user_id(user_id)
        if organizer is None:
            logger.warning("User has no organizer role", user_id=user_id)
            raise AccessDeniedError(message="Only organizers can list competitions")

        logger.debug(
            "Listing competitions",
            user_id=user_id,
            page=input_data.page,
            sort_by=input_data.sort_by,
            sort_order=input_data.sort_order,
            is_archived=input_data.is_archived,
            search=input_data.search,
            page_size=PAGE_SIZE,
            organizer_id=organizer.id,
        )
        items, total = await self.competition_gateway.list_for_organizer(
            organizer.id,
            page=input_data.page,
            page_size=PAGE_SIZE,
            sort_by=input_data.sort_by,
            sort_order=input_data.sort_order,
            is_archived=input_data.is_archived,
            search=input_data.search,
        )

        return CompetitionsList(items=items, total=total, page=input_data.page)
