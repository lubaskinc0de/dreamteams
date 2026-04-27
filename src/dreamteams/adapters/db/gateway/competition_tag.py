from typing import override

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.elements import ColumnElement

from dreamteams.adapters.db.models.competition import competition_tag_table
from dreamteams.application.common.gateway.competition_tag import CompetitionTagGateway
from dreamteams.entities.common.identifiers import CompetitionTagId
from dreamteams.entities.competition.tag import CompetitionTag


class SACompetitionTagGateway(CompetitionTagGateway):
    """SQLAlchemy-based implementation of CompetitionTagGateway."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @override
    async def get(self, tag_id: CompetitionTagId) -> CompetitionTag | None:
        """Retrieve a competition tag by ID."""
        return await self._session.get(CompetitionTag, tag_id)

    @override
    async def get_by_value(self, value: str) -> CompetitionTag | None:
        """Retrieve a competition tag by case-insensitive value."""
        query = select(CompetitionTag).where(func.lower(competition_tag_table.c.value) == value.strip().lower())
        result = await self._session.scalars(query)
        return result.first()

    @override
    async def get_many(self, tag_ids: list[CompetitionTagId]) -> list[CompetitionTag]:
        """Retrieve all tags matching the provided IDs."""
        if not tag_ids:
            return []
        query = select(CompetitionTag).where(competition_tag_table.c.id.in_(tag_ids))
        result = await self._session.scalars(query)
        return list(result.all())

    @override
    async def list(
        self,
        *,
        page: int,
        page_size: int,
        search: str | None,
    ) -> tuple[list[CompetitionTag], int]:
        """List tags with optional search and pagination."""
        filters: list[ColumnElement[bool]] = []
        value_lower = func.lower(competition_tag_table.c.value)
        order_by: list[ColumnElement[object]] = [value_lower, competition_tag_table.c.id]
        if search is not None:
            search_value = search.strip().lower()
            if search_value:
                filters.append(value_lower.contains(search_value))

        count_query = select(func.count()).select_from(competition_tag_table).where(*filters)
        total = (await self._session.execute(count_query)).scalar_one()

        query = (
            select(CompetitionTag).where(*filters).order_by(*order_by).limit(page_size).offset((page - 1) * page_size)
        )
        result = await self._session.scalars(query)
        return list(result.all()), total
