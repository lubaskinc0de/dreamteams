from opentelemetry import metrics

from dreamteams_exporter.application.common.events import (
    DomainEvent,
    ExportJobCreated,
    ExportJobEnqueued,
    ExportJobFailed,
    ExportJobSucceeded,
)
from dreamteams_exporter.entities.common.vo.application_status import ApplicationStatus

_meter = metrics.get_meter("dreamteams_exporter.business")
_export_jobs_created = _meter.create_counter(
    name="dreamteams_exporter.export_jobs_created",
    description="Export jobs created",
    unit="1",
)
_export_jobs_enqueued = _meter.create_counter(
    name="dreamteams_exporter.export_jobs_enqueued",
    description="Export jobs enqueued for processing",
    unit="1",
)
_export_jobs_completed = _meter.create_counter(
    name="dreamteams_exporter.export_jobs_completed",
    description="Export jobs completed by outcome",
    unit="1",
)
_export_job_duration = _meter.create_histogram(
    name="dreamteams_exporter.export_job_duration",
    description="Export job processing duration",
    unit="s",
)
_export_job_rows = _meter.create_histogram(
    name="dreamteams_exporter.export_job_rows",
    description="Rows written per successful export job",
    unit="1",
)
_export_job_pages = _meter.create_histogram(
    name="dreamteams_exporter.export_job_pages",
    description="Application pages fetched per successful export job",
    unit="1",
)


def _status_label(status: ApplicationStatus | None) -> str:
    return status.value if status is not None else "all"


class ExportJobCreatedMetricsEventHandler:
    """Records export-job creation metrics."""

    async def __call__(self, event: DomainEvent) -> None:
        """Increment the export-job creation counter."""
        if not isinstance(event, ExportJobCreated):
            msg = f"{type(self).__name__} received invalid event: {type(event).__name__}"
            raise TypeError(msg)
        _export_jobs_created.add(1, {"application_status": _status_label(event.application_status)})


class ExportJobEnqueuedMetricsEventHandler:
    """Records export-job enqueue metrics."""

    async def __call__(self, event: DomainEvent) -> None:
        """Increment the export-job enqueue counter."""
        if not isinstance(event, ExportJobEnqueued):
            msg = f"{type(self).__name__} received invalid event: {type(event).__name__}"
            raise TypeError(msg)
        _export_jobs_enqueued.add(1, {"application_status": _status_label(event.application_status)})


class ExportJobSucceededMetricsEventHandler:
    """Records successful export-job processing metrics."""

    async def __call__(self, event: DomainEvent) -> None:
        """Record successful export-job counters and histograms."""
        if not isinstance(event, ExportJobSucceeded):
            msg = f"{type(self).__name__} received invalid event: {type(event).__name__}"
            raise TypeError(msg)
        attrs = {
            "application_status": _status_label(event.application_status),
            "outcome": "success",
        }
        status_attrs = {"application_status": _status_label(event.application_status)}
        _export_jobs_completed.add(1, attrs)
        _export_job_duration.record(event.duration_seconds, attrs)
        _export_job_rows.record(event.rows_count, status_attrs)
        _export_job_pages.record(event.pages_count, status_attrs)


class ExportJobFailedMetricsEventHandler:
    """Records failed export-job processing metrics."""

    async def __call__(self, event: DomainEvent) -> None:
        """Record failed export-job counters and duration."""
        if not isinstance(event, ExportJobFailed):
            msg = f"{type(self).__name__} received invalid event: {type(event).__name__}"
            raise TypeError(msg)
        attrs = {
            "application_status": _status_label(event.application_status),
            "outcome": event.outcome,
        }
        _export_jobs_completed.add(1, attrs)
        _export_job_duration.record(event.duration_seconds, attrs)
