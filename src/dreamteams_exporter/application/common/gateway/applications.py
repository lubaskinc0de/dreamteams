from abc import abstractmethod
from typing import Protocol

from dreamteams_exporter.application.common.dto.application import ApplicationsPage
from dreamteams_exporter.entities.common.identifiers import CompetitionId
from dreamteams_exporter.entities.common.vo.application_status import ApplicationStatus


class ApplicationsGateway(Protocol):
    """Reads applications filtered by competition and status, one page at a time."""

    @abstractmethod
    async def list(
        self,
        *,
        competition_id: CompetitionId,
        status: ApplicationStatus,
        page: int,
        page_size: int,
    ) -> ApplicationsPage:
        """Returns page N of applications for the given competition + status."""
        raise NotImplementedError
