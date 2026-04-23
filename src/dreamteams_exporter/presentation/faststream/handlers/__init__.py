from faststream.nats import NatsBroker

from dreamteams_exporter.presentation.faststream.handlers.process_job import router as process_job_router


def include_handlers(broker: NatsBroker) -> None:
    """Attach every FastStream subscriber router to the given NATS broker."""
    broker.include_router(process_job_router)


__all__ = ["include_handlers"]
