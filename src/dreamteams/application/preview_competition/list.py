
from pydantic import BaseModel, Field

from dreamteams.application.common.gateway.competition import CompetitionGateway, CompetitionSortBy
from dreamteams.application.common.gateway.sorting import SortOrder
from dreamteams.application.common.interactor import interactor
from dreamteams.application.manage_competitions.read import CompetitionModel

PAGE_SIZE = 10


class PreviewCompetitionsInput(BaseModel):
    """Input parameters for listing preview competitions."""

    page: int = Field(ge=1, default=1)


class PreviewCompetitionsList(BaseModel):
    """Response model containing paginated list of preview competitions."""

    items: list[CompetitionModel]
    total: int
    page: int


@interactor
class PreviewCompetitions:
    """Interactor for listing preview competitions."""

    competition_gateway: CompetitionGateway

    async def execute(self, input_data: PreviewCompetitionsInput) -> PreviewCompetitionsList:
        """Interactor for viewing competitions as anonymous user"""
        competitions, total = await self.competition_gateway.list(
            organizer_id=None,
            page=input_data.page,
            page_size=PAGE_SIZE,
            sort_by=CompetitionSortBy.CREATED_AT,
            sort_order=SortOrder.DESC,
            is_archived=False,
            search=None,
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
                is_archived=competition.is_archived,
                created_at=competition.created_at,
                updated_at=competition.updated_at,
            )
            for competition in competitions
        ]

        return PreviewCompetitionsList(items=items, total=total, page=input_data.page)
