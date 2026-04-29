from collections.abc import Mapping
from dataclasses import dataclass

from dreamteams_exporter.adapters.event_bus import EventHandler
from dreamteams_exporter.adapters.metrics import (
    ExportJobCreatedMetricsEventHandler,
    ExportJobEnqueuedMetricsEventHandler,
    ExportJobFailedMetricsEventHandler,
    ExportJobSucceededMetricsEventHandler,
)
from dreamteams_exporter.application.common.events import (
    DomainEvent,
    ExportJobCreated,
    ExportJobEnqueued,
    ExportJobFailed,
    ExportJobSucceeded,
)


@dataclass(frozen=True, slots=True)
class EventHandlersRegistry:
    """Registry of exporter event handlers by event class."""

    export_job_created_metrics_handler: ExportJobCreatedMetricsEventHandler
    export_job_enqueued_metrics_handler: ExportJobEnqueuedMetricsEventHandler
    export_job_succeeded_metrics_handler: ExportJobSucceededMetricsEventHandler
    export_job_failed_metrics_handler: ExportJobFailedMetricsEventHandler

    def as_mapping(self) -> Mapping[type[DomainEvent], tuple[EventHandler, ...]]:
        """Return exporter event handlers keyed by supported event type."""
        return {
            ExportJobCreated: (self.export_job_created_metrics_handler,),
            ExportJobEnqueued: (self.export_job_enqueued_metrics_handler,),
            ExportJobSucceeded: (self.export_job_succeeded_metrics_handler,),
            ExportJobFailed: (self.export_job_failed_metrics_handler,),
        }
