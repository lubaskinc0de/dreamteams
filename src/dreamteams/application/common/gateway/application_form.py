from abc import abstractmethod
from typing import Protocol

from dreamteams.entities.application_form.entity import ApplicationForm
from dreamteams.entities.common.identifiers import CompetitionId


class ApplicationFormGateway(Protocol):
    """Protocol defining the interface for reading ApplicationForm data from persistent storage."""

    @abstractmethod
    async def get_by_competition_id(self, competition_id: CompetitionId) -> ApplicationForm | None:
        """
        Retrieve the application form for a given competition.

        Returns None if not found or if the competition's organizer account is blocked.
        Implementations must exclude forms whose organizer has ``ban_status.is_blocked = True``.
        """
        raise NotImplementedError
