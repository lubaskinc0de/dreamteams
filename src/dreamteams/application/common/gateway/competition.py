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
    async def get(
        self,
        competition_id: CompetitionId,
        *,
        eager_milestones: bool = False,
    ) -> Competition | None:
        """Retrieves a competition entity by its unique identifier, returns None if not found.

        Set ``eager_milestones=True`` when the caller renders milestones in its response —
        otherwise the relationship raises on access.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_with_organizer(self, competition_id: CompetitionId) -> Competition | None:
        """Retrieves a competition with the organizer (and organizer.user) eagerly loaded."""
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
        active: bool | None,
        eager_organizer: bool = False,
        eager_milestones: bool = False,
    ) -> tuple[list[Competition], int]:
        """List competitions by organizer with pagination and sorting.

        Returns tuple of (competitions list, total count). When ``eager_organizer`` is True
        the competition's organizer (and organizer.user) is eagerly loaded; when
        ``eager_milestones`` is True the competition's milestones are eagerly loaded.
        """
        raise NotImplementedError
