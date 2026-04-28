import structlog
from pydantic import BaseModel, Field

from dreamteams.application.common.dto.preview_competition import (  # noqa: F401
    PreviewCompetitionModel,
    PreviewOrganizerModel,
)
from dreamteams.application.common.gateway.competition import CompetitionGateway
from dreamteams_common.interactor import interactor
from dreamteams_common.logger import Logger

PAGE_SIZE = 10
logger: Logger = structlog.get_logger(__name__)


class PreviewCompetitionsInput(BaseModel):
    """Input parameters for listing preview competitions."""

    page: int = Field(ge=1, default=1)


class PreviewCompetitionsList(BaseModel):
    """Response model containing paginated list of preview competitions."""

    items: list[PreviewCompetitionModel]
    total: int
    page: int


@interactor
class PreviewCompetitions:
    """Interactor for listing preview competitions as anonymous user."""

    competition_gateway: CompetitionGateway

    async def execute(self, input_data: PreviewCompetitionsInput) -> PreviewCompetitionsList:
        """Browse competitions as anonymous user."""
        logger.info("Preview competitions called", page_size=PAGE_SIZE, page=input_data.page)
        items, total = await self.competition_gateway.list_preview(
            page=input_data.page,
            page_size=PAGE_SIZE,
        )
        return PreviewCompetitionsList(items=items, total=total, page=input_data.page)
