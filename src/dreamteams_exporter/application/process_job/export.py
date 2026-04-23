from dataclasses import dataclass

import structlog

from dreamteams_common.clock import Clock
from dreamteams_common.errors import AppError
from dreamteams_common.interactor import interactor
from dreamteams_common.logger import Logger
from dreamteams_common.uow import UoW
from dreamteams_exporter.application.common.gateway.applications import ApplicationsGateway
from dreamteams_exporter.application.common.gateway.export_job import ExportJobGateway
from dreamteams_exporter.application.common.idp import IdProvider
from dreamteams_exporter.application.common.rate_limiter import ExportRateLimiter
from dreamteams_exporter.application.common.spreadsheet_exporter import SpreadsheetExporter
from dreamteams_exporter.application.errors.job import JobNotFoundError
from dreamteams_exporter.entities.common.identifiers import ExportJobId
from dreamteams_exporter.entities.errors.user import InvalidRoleError
from dreamteams_exporter.entities.export_job.entity import ExportApplicationsJob

_PAGE_SIZE = 100


@dataclass(slots=True, kw_only=True, frozen=True)
class ProcessExportJobInput:
    """Payload accepted by the process-job interactor."""

    job_id: ExportJobId


logger: Logger = structlog.get_logger(__name__)


@interactor
class ExportApplicationsToSheets:
    """Interactor that builds the Excel export for a previously-created job and persists it."""

    uow: UoW
    idp: IdProvider
    job_gateway: ExportJobGateway
    applications_gateway: ApplicationsGateway
    rate_limiter: ExportRateLimiter
    spreadsheet_exporter: SpreadsheetExporter
    clock: Clock

    async def execute(self, data: ProcessExportJobInput) -> None:
        """Build the spreadsheet for the given job, stream it out, and mark the job succeeded or failed."""
        user = await self.idp.get_user()
        if user.organizer_id is None:
            raise InvalidRoleError(message="Only organizers may export applications")

        await self.rate_limiter.check_and_record(user.user_id)

        job = await self.job_gateway.get(data.job_id)
        if job is None:
            raise JobNotFoundError

        try:
            url = await self._stream_to_spreadsheet(job)
        except AppError as exc:
            logger.warning("Export failed with domain error", job_id=job.id, code=exc.code)
            job.mark_failed(str(exc), self.clock)
            await self.uow.commit()
            raise
        except Exception as exc:
            logger.exception("Export failed with unexpected error", job_id=job.id)
            job.mark_failed(f"unexpected: {type(exc).__name__}", self.clock)
            await self.uow.commit()
            raise

        job.mark_success(url, self.clock)
        await self.uow.commit()
        logger.info("Export finished", job_id=job.id, file_url=url)

    async def _stream_to_spreadsheet(self, job: ExportApplicationsJob) -> str:
        session = await self.spreadsheet_exporter.start(key=f"exports/{job.id}.csv")
        try:
            page = 1
            while True:
                batch = await self.applications_gateway.list(
                    competition_id=job.competition_id,
                    status=job.application_status,
                    page=page,
                    page_size=_PAGE_SIZE,
                )
                await session.write_rows(batch.items)
                if not batch.has_next:
                    break
                page += 1
        except BaseException:
            await session.abort()
            raise
        return await session.finish()
