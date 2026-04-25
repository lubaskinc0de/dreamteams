from dataclasses import dataclass
from uuid import UUID

import structlog
from dishka_faststream import FromDishka, inject
from faststream.nats import NatsRouter, PullSub

from dreamteams_common.logger import Logger
from dreamteams_exporter.application.export_applications_sheets.process import (
    ExportApplicationsToSheets,
    ProcessExportJobInput,
)

logger: Logger = structlog.get_logger(__name__)

router = NatsRouter()

PROCESS_SUBJECT = "exporter.jobs.process"
PROCESS_STREAM = "exporter"
PROCESS_CONSUMER = "exporter-worker"


@dataclass(slots=True, frozen=True, kw_only=True)
class ProcessJobMessage:
    """Payload schema for the ``exporter.jobs.process`` subject."""

    job_id: UUID


@router.subscriber(  # type: ignore[untyped-decorator]
    PROCESS_SUBJECT,
    stream=PROCESS_STREAM,
    durable=PROCESS_CONSUMER,
    pull_sub=PullSub(batch_size=1),
)
@inject
async def handle_process_job(
    message: ProcessJobMessage,
    interactor: FromDishka[ExportApplicationsToSheets],
) -> None:
    """Consumes one ``exporter.jobs.process`` message and runs the long-running export interactor."""
    logger.info("Received process-job message", job_id=message.job_id)
    await interactor.execute(ProcessExportJobInput(job_id=message.job_id))
