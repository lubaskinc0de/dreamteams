from abc import abstractmethod
from typing import Protocol

from dreamteams.entities.application_form.entity import ApplicationForm
from dreamteams.entities.common.identifiers import CompetitionId


class ApplicationFormCache(Protocol):
    """Adapter-local cache port for application form read-through decoration."""

    @abstractmethod
    async def get(self, competition_id: CompetitionId) -> ApplicationForm | None:
        """Return cached form for the competition, or None on miss/error."""
        raise NotImplementedError

    @abstractmethod
    async def set(self, competition_id: CompetitionId, form: ApplicationForm) -> None:
        """Store a form for the competition."""
        raise NotImplementedError

    @abstractmethod
    async def delete(self, competition_id: CompetitionId) -> None:
        """Delete one competition form cache entry."""
        raise NotImplementedError

    @abstractmethod
    async def clear(self) -> None:
        """Clear every application form cache entry."""
        raise NotImplementedError
