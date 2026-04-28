from abc import abstractmethod
from typing import Protocol


class CompetitionTagCache(Protocol):
    """Invalidation port for cached competition tags."""

    @abstractmethod
    async def clear(self) -> None:
        """Clear every tag cache entry."""
        raise NotImplementedError
