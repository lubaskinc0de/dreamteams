from typing import override

from dreamteams.adapters.cache.common.competition_tag_read_cache import CompetitionTagReadCache
from dreamteams.application.common.gateway.competition_tag import CompetitionTagGateway
from dreamteams.entities.common.identifiers import CompetitionTagId
from dreamteams.entities.competition.tag import CompetitionTag


class CachedCompetitionTagGateway(CompetitionTagGateway):
    """Competition tag gateway decorator for cache-safe read paths."""

    def __init__(
        self,
        wrapped: CompetitionTagGateway,
        cache: CompetitionTagReadCache,
    ) -> None:
        self._wrapped = wrapped
        self._cache = cache

    @override
    async def get(self, tag_id: CompetitionTagId) -> CompetitionTag | None:
        """Delegate ID lookup to preserve session-attached entities for write paths."""
        return await self._wrapped.get(tag_id)

    @override
    async def get_by_value(self, value: str) -> CompetitionTag | None:
        """Fetch a tag by value."""
        return await self._wrapped.get_by_value(value)

    @override
    async def get_many(self, tag_ids: list[CompetitionTagId]) -> list[CompetitionTag]:
        """Delegate bulk lookup to preserve session-attached entities for relationships."""
        return await self._wrapped.get_many(tag_ids)

    @override
    async def list(
        self,
        *,
        page: int,
        page_size: int,
        search: str | None,
    ) -> tuple[list[CompetitionTag], int]:
        """List tags, using cache for list pages."""
        cached = await self._cache.get_list(page=page, page_size=page_size, search=search)
        if cached is not None:
            return cached

        items, total = await self._wrapped.list(page=page, page_size=page_size, search=search)
        await self._cache.set_list(page=page, page_size=page_size, search=search, items=items, total=total)
        return items, total
