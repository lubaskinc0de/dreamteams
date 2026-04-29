from abc import abstractmethod
from typing import Protocol

from dreamteams.entities.competition.tag import CompetitionTag


class CompetitionTagReadCache(Protocol):
    """Adapter-local cache port for safe read-through tag gateway methods."""

    @abstractmethod
    async def get_by_value(self, value: str) -> CompetitionTag | None:
        """Return a cached tag by normalized value, or None on miss/error."""
        raise NotImplementedError

    @abstractmethod
    async def set_by_value(self, value: str, tag: CompetitionTag) -> None:
        """Store a tag by normalized value."""
        raise NotImplementedError

    @abstractmethod
    async def get_list(
        self,
        *,
        page: int,
        page_size: int,
        search: str | None,
    ) -> tuple[list[CompetitionTag], int] | None:
        """Return a cached tag list page, or None on miss/error."""
        raise NotImplementedError

    @abstractmethod
    async def set_list(
        self,
        *,
        page: int,
        page_size: int,
        search: str | None,
        items: list[CompetitionTag],
        total: int,
    ) -> None:
        """Store a tag list page."""
        raise NotImplementedError

    @abstractmethod
    async def clear(self) -> None:
        """Clear every tag cache entry."""
        raise NotImplementedError
