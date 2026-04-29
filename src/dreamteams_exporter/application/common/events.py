from abc import ABC
from dataclasses import dataclass

from dreamteams_exporter.entities.common.vo.application_status import ApplicationStatus


class DomainEvent(ABC):  # noqa: B024
    """Base class for exporter domain events published by application use cases."""


@dataclass(frozen=True, slots=True, kw_only=True)
class ExportJobCreated(DomainEvent):
    """Event emitted when an export job is created."""

    application_status: ApplicationStatus | None


@dataclass(frozen=True, slots=True, kw_only=True)
class ExportJobEnqueued(DomainEvent):
    """Event emitted when an export job is enqueued for processing."""

    application_status: ApplicationStatus | None


@dataclass(frozen=True, slots=True, kw_only=True)
class ExportJobSucceeded(DomainEvent):
    """Event emitted when an export job finishes successfully."""

    application_status: ApplicationStatus | None
    duration_seconds: float
    rows_count: int
    pages_count: int


@dataclass(frozen=True, slots=True, kw_only=True)
class ExportJobFailed(DomainEvent):
    """Event emitted when an export job fails during processing."""

    application_status: ApplicationStatus | None
    duration_seconds: float
    outcome: str
