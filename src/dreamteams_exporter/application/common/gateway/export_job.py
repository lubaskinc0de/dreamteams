from abc import abstractmethod
from typing import Protocol

from dreamteams_exporter.application.common.dto.export_job import ExportJobModel
from dreamteams_exporter.entities.common.identifiers import ExportJobId
from dreamteams_exporter.entities.export_job.entity import ExportApplicationsJob


class ExportJobGateway(Protocol):
    """Persists and reads export jobs from the exporter's durable store."""

    @abstractmethod
    async def create(self, job: ExportApplicationsJob) -> None:
        """Creates a new pending export job."""
        raise NotImplementedError

    @abstractmethod
    async def get(self, job_id: ExportJobId) -> ExportApplicationsJob | None:
        """Loads the mutable aggregate for update; returns None if no job matches."""
        raise NotImplementedError

    @abstractmethod
    async def read(self, job_id: ExportJobId) -> ExportJobModel | None:
        """Loads the read model; returns None if no job matches."""
        raise NotImplementedError

    @abstractmethod
    async def save(self, job: ExportApplicationsJob) -> None:
        """Persists the updated aggregate."""
        raise NotImplementedError
