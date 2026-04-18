from abc import abstractmethod
from enum import StrEnum, auto
from typing import Protocol

from dreamteams.application.common.gateway.sorting import SortOrder
from dreamteams.entities.application.entity import Application, ApplicationStatus
from dreamteams.entities.common.identifiers import ApplicationId, CompetitionId, ParticipantId


class ApplicationSortBy(StrEnum):
    """Fields available for sorting applications."""

    CREATED_AT = auto()


class ApplicationGateway(Protocol):
    """Protocol defining the interface for reading Application data from persistent storage."""

    @abstractmethod
    async def get(self, application_id: ApplicationId) -> Application | None:
        """Retrieve an application by its unique identifier, returns None if not found."""
        raise NotImplementedError

    @abstractmethod
    async def get_by_participant_and_competition(
        self,
        participant_id: ParticipantId,
        competition_id: CompetitionId,
    ) -> Application | None:
        """Retrieve an application by participant and competition, returns None if not found."""
        raise NotImplementedError

    @abstractmethod
    async def list_by_competition(  # noqa: PLR0913
        self,
        competition_id: CompetitionId,
        *,
        page: int,
        page_size: int,
        sort_by: ApplicationSortBy,
        sort_order: SortOrder,
        status: ApplicationStatus | None,
    ) -> tuple[list[Application], int]:
        """List applications for a competition with pagination, sorting, and optional status filter.

        Returns tuple of (applications list, total count).
        """
        raise NotImplementedError

    @abstractmethod
    async def list_by_participant(  # noqa: PLR0913
        self,
        participant_id: ParticipantId,
        *,
        page: int,
        page_size: int,
        sort_by: ApplicationSortBy,
        sort_order: SortOrder,
        status: ApplicationStatus | None,
    ) -> tuple[list[Application], int]:
        """List applications submitted by a participant with pagination, sorting, and optional status filter.

        Returns tuple of (applications list, total count).
        """
        raise NotImplementedError

    @abstractmethod
    async def count_accepted_by_competition(self, competition_id: CompetitionId) -> int:
        """Count applications with ACCEPTED status for a given competition."""
        raise NotImplementedError
