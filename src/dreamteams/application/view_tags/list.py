from pydantic import BaseModel, Field

from dreamteams.application.common.gateway.competition_tag import CompetitionTagGateway
from dreamteams.application.common.gateway.user import UserGateway
from dreamteams.application.common.idp import IdProvider
from dreamteams.application.common.interactor import interactor
from dreamteams.application.errors.user import UserNotFoundError
from dreamteams.entities.competition.tag import CompetitionTag
from dreamteams.entities.errors.base import AccessDeniedError

PAGE_SIZE = 30


class ListCompetitionTagsInput(BaseModel):
    """Input parameters for listing competition tags."""

    page: int = Field(ge=1, default=1)
    search: str | None = None


class CompetitionTagsList(BaseModel):
    """Paginated list of competition tags."""

    items: list[CompetitionTag]
    total: int
    page: int


@interactor
class ListCompetitionTags:
    """Interactor for listing competition tags as a participant or organizer."""

    idp: IdProvider
    user_gateway: UserGateway
    competition_tag_gateway: CompetitionTagGateway

    async def execute(self, input_data: ListCompetitionTagsInput) -> CompetitionTagsList:
        """List competition tags."""
        user_id = await self.idp.get_user_id()
        user = await self.user_gateway.get_with_roles(user_id)
        if user is None:
            raise UserNotFoundError(user_id=user_id)
        if user.organizer is None and user.participant is None:
            raise AccessDeniedError(message="Only participants and organizers can view tags")

        items, total = await self.competition_tag_gateway.list(
            page=input_data.page,
            page_size=PAGE_SIZE,
            search=input_data.search,
        )
        return CompetitionTagsList(items=items, total=total, page=input_data.page)
