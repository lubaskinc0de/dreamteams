from pydantic import BaseModel, Field

from dreamteams.application.block_user.shared import ensure_admin
from dreamteams.application.common.gateway.competition_tag import CompetitionTagGateway
from dreamteams.application.common.gateway.user import UserGateway
from dreamteams.application.common.idp import IdProvider
from dreamteams.application.common.input_limits import MAX_PAGE, MAX_SEARCH_LENGTH
from dreamteams.entities.competition.tag import CompetitionTag
from dreamteams_common.interactor import interactor

PAGE_SIZE = 30


class ListCompetitionTagsInput(BaseModel):
    """Input parameters for listing competition tags."""

    page: int = Field(ge=1, le=MAX_PAGE, default=1)
    search: str | None = Field(default=None, max_length=MAX_SEARCH_LENGTH)


class CompetitionTagsList(BaseModel):
    """Paginated list of competition tags."""

    items: list[CompetitionTag]
    total: int
    page: int


@interactor
class ListCompetitionTags:
    """Interactor for listing competition tags as an admin."""

    idp: IdProvider
    user_gateway: UserGateway
    competition_tag_gateway: CompetitionTagGateway

    async def execute(self, input_data: ListCompetitionTagsInput) -> CompetitionTagsList:
        """List competition tags."""
        admin_user_id = await self.idp.get_user_id()
        admin = await self.user_gateway.get(admin_user_id)
        ensure_admin(admin, admin_user_id)

        items, total = await self.competition_tag_gateway.list(
            page=input_data.page,
            page_size=PAGE_SIZE,
            search=input_data.search,
        )
        return CompetitionTagsList(items=items, total=total, page=input_data.page)
