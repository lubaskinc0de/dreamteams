from abc import abstractmethod
from typing import Protocol

from dreamteams_exporter.application.common.events import DomainEvent
from dreamteams_exporter.entities.common.identifiers import ExportJobId


class EventBus(Protocol):
    """Publishes exporter-local domain events."""

    @abstractmethod
    async def publish(self, event: DomainEvent) -> None:
        """Publish a domain event."""
        raise NotImplementedError


class JobEventBus(Protocol):
    """Publishes follow-up events for an export job (e.g. process-job trigger)."""

    @abstractmethod
    async def publish_process(self, job_id: ExportJobId) -> None:
        """Publishes a message that triggers the process step for the given job."""
        raise NotImplementedError
