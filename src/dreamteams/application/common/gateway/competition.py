from abc import abstractmethod
from enum import StrEnum, auto
from typing import Protocol

from dreamteams.application.common.gateway.sorting import SortOrder
from dreamteams.entities.common.identifiers import CompetitionId, OrganizerId
from dreamteams.entities.competition.entity import Competition


class CompetitionSortBy(StrEnum):
    """Fields available for sorting competitions."""

    CREATED_AT = auto()
    TITLE = auto()
    REGISTRATION_START = auto()
    TEAM_FORMATION_START = auto()


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

    @abstractmethod
    async def list(  # noqa: PLR0913
        self,
        organizer_id: OrganizerId | None = None,
        *,
        page: int,
        page_size: int,
        sort_by: CompetitionSortBy,
        sort_order: SortOrder,
        is_archived: bool | None,
        search: str | None,
        active: bool,
    ) -> tuple[list[Competition], int]:
        """List competitions by organizer with pagination and sorting.

        Returns tuple of (competitions list, total count).
        """
        raise NotImplementedError
