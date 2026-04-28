from abc import abstractmethod
from typing import Protocol

from dreamteams.entities.common.identifiers import CompetitionId


class CompetitionCache(Protocol):
    """Invalidation port for cached competition read models."""

    @abstractmethod
    async def delete_read(self, competition_id: CompetitionId) -> None:
        """Delete one single-competition read model entry."""
        raise NotImplementedError

    @abstractmethod
    async def clear_read(self) -> None:
        """Clear all single-competition read model entries."""
        raise NotImplementedError

    @abstractmethod
    async def clear_preview(self) -> None:
        """Clear every anonymous preview page entry."""
        raise NotImplementedError
