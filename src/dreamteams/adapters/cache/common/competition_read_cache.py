from abc import abstractmethod
from typing import Protocol

from dreamteams.application.common.dto.competition import CompetitionModel
from dreamteams.entities.common.identifiers import CompetitionId


class CompetitionReadCache(Protocol):
    """Adapter-local cache port for read-through competition gateway decoration."""

    @abstractmethod
    async def get_read(self, competition_id: CompetitionId) -> CompetitionModel | None:
        """Return a cached single-competition read model, or None on miss/error."""
        raise NotImplementedError

    @abstractmethod
    async def set_read(self, competition_id: CompetitionId, model: CompetitionModel) -> None:
        """Store a single-competition read model."""
        raise NotImplementedError

    @abstractmethod
    async def delete_read(self, competition_id: CompetitionId) -> None:
        """Delete one single-competition read model entry."""
        raise NotImplementedError

    @abstractmethod
    async def clear_read(self) -> None:
        """Clear all single-competition read model entries."""
        raise NotImplementedError
