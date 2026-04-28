from abc import abstractmethod
from typing import Protocol

from dreamteams.application.common.dto.competition import CompetitionModel
from dreamteams.application.common.dto.preview_competition import PreviewCompetitionModel
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
    async def get_preview(self, *, page: int, page_size: int) -> tuple[list[PreviewCompetitionModel], int] | None:
        """Return a cached anonymous preview page, or None on miss/error."""
        raise NotImplementedError

    @abstractmethod
    async def set_preview(self, *, page: int, page_size: int, items: list[PreviewCompetitionModel], total: int) -> None:
        """Store an anonymous preview page."""
        raise NotImplementedError
