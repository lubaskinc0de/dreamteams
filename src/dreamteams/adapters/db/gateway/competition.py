from typing import override

from sqlalchemy import and_, delete, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from dreamteams.adapters.db.models import competition_table, milestone_table
from dreamteams.application.common.gateway.competition import CompetitionGateway, CompetitionSortBy
from dreamteams.application.common.gateway.sorting import SortOrder
from dreamteams.entities.common.identifiers import CompetitionId, OrganizerId
from dreamteams.entities.competition.entity import Competition
from dreamteams.entities.competition.milestone import Milestone


class SACompetitionGateway(CompetitionGateway):
    """SQLAlchemy-based implementation of CompetitionGateway for reading competition entities."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @override
    async def get(self, competition_id: CompetitionId) -> Competition | None:
        """Queries the database for a competition by ID using SQLAlchemy session, returns None if not found."""
        return await self._session.get(Competition, competition_id)

    @override
    async def clear_milestones(self, competition_id: CompetitionId) -> None:
        """Delete all competition milestones from storage."""
        q = delete(Milestone).where(milestone_table.c.competition_id == competition_id)
        await self._session.execute(q)

    @override
    async def list_by_organizer(
        self,
        organizer_id: OrganizerId,
        *,
        page: int,
        page_size: int,
        sort_by: CompetitionSortBy,
        sort_order: SortOrder,
        is_archived: bool | None,
    ) -> tuple[list[Competition], int]:
        """List competitions by organizer with pagination and sorting."""
        sort_column = {
            CompetitionSortBy.CREATED_AT: competition_table.c.created_at,
            CompetitionSortBy.TITLE: competition_table.c.title,
            CompetitionSortBy.REGISTRATION_START: competition_table.c.registration_start,
            CompetitionSortBy.TEAM_FORMATION_START: competition_table.c.team_formation_start,
        }[sort_by]

        order = desc(sort_column) if sort_order == SortOrder.DESC else sort_column
        filters = competition_table.c.organizer_id == organizer_id

        if is_archived is not None:
            filters = and_(filters, competition_table.c.is_archived == is_archived)

        count_query = select(func.count()).where(filters)
        total = await self._session.scalar(count_query) or 0

        query = (
            select(Competition)
            .where(filters)
            .order_by(order, desc(competition_table.c.id) if sort_order == SortOrder.DESC else competition_table.c.id)
            .limit(page_size)
            .offset((page - 1) * page_size)
        )

        result = await self._session.scalars(query)
        competitions = list(result.all())

        return competitions, total
