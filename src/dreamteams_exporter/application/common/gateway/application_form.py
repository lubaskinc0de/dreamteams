from abc import abstractmethod
from typing import Protocol

from dreamteams_exporter.entities.application_form.entity import ApplicationForm
from dreamteams_exporter.entities.common.identifiers import CompetitionId


class ApplicationFormGateway(Protocol):
    """Reads a competition's application form."""

    @abstractmethod
    async def get_by_competition_id(self, competition_id: CompetitionId) -> ApplicationForm | None:
        """Return the application form for a competition, or None when no form exists."""
        raise NotImplementedError
