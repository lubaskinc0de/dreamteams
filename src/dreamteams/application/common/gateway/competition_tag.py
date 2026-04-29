from abc import abstractmethod
from typing import Protocol

from dreamteams.entities.common.identifiers import CompetitionTagId
from dreamteams.entities.competition.tag import CompetitionTag


class CompetitionTagGateway(Protocol):
    """Protocol for reading and managing competition tags."""

    @abstractmethod
    async def get(self, tag_id: CompetitionTagId) -> CompetitionTag | None:
        """Retrieve a competition tag by ID."""
        raise NotImplementedError

    @abstractmethod
    async def get_by_value(self, value: str) -> CompetitionTag | None:
        """Retrieve a competition tag by case-insensitive value."""
        raise NotImplementedError

    @abstractmethod
    async def get_many(self, tag_ids: list[CompetitionTagId]) -> list[CompetitionTag]:
        """Retrieve all tags matching the provided IDs."""
        raise NotImplementedError

    @abstractmethod
    async def list(
        self,
        *,
        page: int,
        page_size: int,
        search: str | None,
    ) -> tuple[list[CompetitionTag], int]:
        """List tags with optional search and pagination."""
        raise NotImplementedError
