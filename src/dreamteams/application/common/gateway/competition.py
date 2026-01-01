from abc import abstractmethod
from typing import Protocol

from dreamteams.entities.common.identifiers import CompetitionId
from dreamteams.entities.competition.entity import Competition


class CompetitionGateway(Protocol):
    """Protocol defining the interface for reading competition data from persistent storage."""

    @abstractmethod
    async def get(self, competition_id: CompetitionId) -> Competition | None:
        """Retrieves a competition entity by its unique identifier, returns None if not found."""
        raise NotImplementedError

    @abstractmethod
    async def clear_milestones(self, competition_id: CompetitionId) -> None:
        """Delete all competition milestones from storage."""
        raise NotImplementedError
