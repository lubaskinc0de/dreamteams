from abc import abstractmethod
from typing import Protocol

from dreamteams.entities.application.entity import Application
from dreamteams.entities.common.identifiers import ApplicationId, CompetitionId, ParticipantId


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
    async def list_by_competition(
        self,
        competition_id: CompetitionId,
        *,
        page: int,
        page_size: int,
    ) -> tuple[list[Application], int]:
        """List applications for a competition with pagination.

        Returns tuple of (applications list, total count).
        """
        raise NotImplementedError

    @abstractmethod
    async def list_by_participant(
        self,
        participant_id: ParticipantId,
        *,
        page: int,
        page_size: int,
    ) -> tuple[list[Application], int]:
        """List applications submitted by a participant with pagination.

        Returns tuple of (applications list, total count).
        """
        raise NotImplementedError

    @abstractmethod
    async def count_accepted_by_competition(self, competition_id: CompetitionId) -> int:
        """Count applications with ACCEPTED status for a given competition."""
        raise NotImplementedError
