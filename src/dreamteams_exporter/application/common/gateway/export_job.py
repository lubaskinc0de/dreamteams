from abc import abstractmethod
from typing import Protocol

from dreamteams_exporter.application.common.dto.export_job import ExportJobModel
from dreamteams_exporter.entities.common.identifiers import ExportJobId
from dreamteams_exporter.entities.export_job.entity import ExportApplicationsJob


class ExportJobGateway(Protocol):
    """Reads export jobs from persistent storage."""

    @abstractmethod
    async def get(self, job_id: ExportJobId) -> ExportApplicationsJob | None:
        """Loads the mutable aggregate for update; returns None if no row matches."""
        raise NotImplementedError

    @abstractmethod
    async def read(self, job_id: ExportJobId) -> ExportJobModel | None:
        """Loads the read model; returns None if no row matches."""
        raise NotImplementedError
