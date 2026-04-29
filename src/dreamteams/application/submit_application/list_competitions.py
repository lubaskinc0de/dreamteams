import structlog
from pydantic import BaseModel, Field

from dreamteams.application.common.dto.explore_competition import (  # noqa: F401
    ExploreCompetitionModel,
    ExploreOrganizerModel,
)
from dreamteams.application.common.gateway.competition import CompetitionGateway, ExploreSortBy
from dreamteams.application.common.gateway.participant import ParticipantGateway
from dreamteams.application.common.idp import IdProvider
from dreamteams.entities.common.identifiers import CompetitionTagId
from dreamteams.entities.errors.base import AccessDeniedError
from dreamteams_common.interactor import interactor
from dreamteams_common.logger import Logger

PAGE_SIZE = 10
logger: Logger = structlog.get_logger(__name__)


class ExploreCompetitionsInput(BaseModel):
    """Input parameters for participant-facing explore list."""

    page: int = Field(ge=1, default=1)
    sort_by: ExploreSortBy = ExploreSortBy.MOST_POPULAR
    search: str | None = None
    min_team_size: int | None = Field(default=None, ge=1)
    max_team_size: int | None = Field(default=None, ge=1)
    auto_accept: bool | None = None
    tag_ids: list[CompetitionTagId] | None = None


class ExploreCompetitionsList(BaseModel):
    """Response model containing a paginated explore list."""

    items: list[ExploreCompetitionModel]
    total: int
    page: int


@interactor
class ExploreCompetitions:
    """Participant-facing browse with rich filters (actor: participant)."""

    idp: IdProvider
    participant_gateway: ParticipantGateway
    competition_gateway: CompetitionGateway

    async def execute(self, input_data: ExploreCompetitionsInput) -> ExploreCompetitionsList:
        """List competitions available for the current participant to apply to."""
        user_id = await self.idp.get_user_id()
        participant = await self.participant_gateway.get_by_user_id(user_id)
        if participant is None:
            logger.warning("User has no participant profile", user_id=user_id)
            raise AccessDeniedError(message="Only participants can explore competitions")

        logger.debug(
            "Exploring competitions",
            user_id=user_id,
            participant_id=participant.id,
            page=input_data.page,
            sort_by=input_data.sort_by,
            search=input_data.search,
            min_team_size=input_data.min_team_size,
            max_team_size=input_data.max_team_size,
            auto_accept=input_data.auto_accept,
            tag_ids=input_data.tag_ids,
        )

        items, total = await self.competition_gateway.explore(
            participant_id=participant.id,
            participant_type=participant.participant_type,
            page=input_data.page,
            page_size=PAGE_SIZE,
            sort_by=input_data.sort_by,
            search=input_data.search,
            min_team_size=input_data.min_team_size,
            max_team_size=input_data.max_team_size,
            auto_accept=input_data.auto_accept,
            tag_ids=input_data.tag_ids,
        )
        return ExploreCompetitionsList(items=items, total=total, page=input_data.page)
