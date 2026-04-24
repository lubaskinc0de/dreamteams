import json
from dataclasses import dataclass

import structlog

from dreamteams_common.clock import Clock
from dreamteams_common.errors import AppError
from dreamteams_common.interactor import interactor
from dreamteams_common.logger import Logger
from dreamteams_exporter.application.common.dto.export_row import EXPORT_HEADERS, ExportRow
from dreamteams_exporter.application.common.gateway.applications import ApplicationsGateway
from dreamteams_exporter.application.common.gateway.export_job import ExportJobGateway
from dreamteams_exporter.application.common.idp import IdProvider
from dreamteams_exporter.application.common.rate_limiter import ExportRateLimiter
from dreamteams_exporter.application.common.spreadsheet_exporter import SpreadsheetExporter
from dreamteams_exporter.application.errors.job import JobNotFoundError
from dreamteams_exporter.entities.application.entity import Application
from dreamteams_exporter.entities.common.identifiers import ExportJobId
from dreamteams_exporter.entities.common.vo.participant_contact import ParticipantContact
from dreamteams_exporter.entities.export_job.entity import ExportApplicationsJob

_PAGE_SIZE = 100


@dataclass(slots=True, kw_only=True, frozen=True)
class ProcessExportJobInput:
    """Payload accepted by the process-job interactor."""

    job_id: ExportJobId


logger: Logger = structlog.get_logger(__name__)


def _format_contacts(contacts: list[ParticipantContact]) -> str:
    return ", ".join(f"{c.title}: {c.url}" for c in contacts)


def _to_export_row(application: Application) -> ExportRow:
    """Project an Application entity into the flattened row exported to the sheet."""
    return ExportRow(
        application_id=str(application.id),
        competition_name=application.competition_name,
        domains=", ".join(application.domains),
        status=application.status.value,
        created_at=application.created_at.isoformat(),
        form_data=json.dumps(application.form_data, ensure_ascii=False) if application.form_data is not None else "",
        participant_id=str(application.participant.id),
        full_name=application.participant.full_name,
        bio=application.participant.bio or "",
        participant_type=application.participant.participant_type,
        age=str(application.participant.age),
        contacts=_format_contacts(application.participant.contacts),
    )


@interactor
class ExportApplicationsToSheets:
    """Interactor that builds the spreadsheet export for a previously-created job and persists it."""

    idp: IdProvider
    job_gateway: ExportJobGateway
    applications_gateway: ApplicationsGateway
    rate_limiter: ExportRateLimiter
    spreadsheet_exporter: SpreadsheetExporter
    clock: Clock

    async def execute(self, data: ProcessExportJobInput) -> None:
        """Build the spreadsheet for the given job, stream it out, and mark the job succeeded or failed."""
        user = await self.idp.get_user()
        job = await self.job_gateway.get(data.job_id)
        if job is None:
            raise JobNotFoundError

        try:
            await self.rate_limiter.check_and_record(user.user_id)
            url = await self._stream_to_spreadsheet(job)
        except AppError as exc:
            logger.warning("Export failed with domain error", job_id=job.id, code=exc.code)
            job.mark_failed(str(exc), self.clock)
            await self.job_gateway.save(job)
            raise
        except Exception as exc:
            logger.exception("Export failed with unexpected error", job_id=job.id)
            job.mark_failed(f"unexpected: {type(exc).__name__}", self.clock)
            await self.job_gateway.save(job)
            raise

        job.mark_success(url, self.clock)
        await self.job_gateway.save(job)
        logger.info("Export finished", job_id=job.id, file_url=url)

    async def _stream_to_spreadsheet(self, job: ExportApplicationsJob) -> str:
        session = await self.spreadsheet_exporter.start(
            key=f"exports/{job.id}.csv",
            headers=EXPORT_HEADERS,
        )
        try:
            page = 1
            while True:
                batch = await self.applications_gateway.list(
                    competition_id=job.competition_id,
                    status=job.application_status,
                    page=page,
                    page_size=_PAGE_SIZE,
                )
                await session.write_rows(_to_export_row(app) for app in batch.items)
                if not batch.has_next:
                    break
                page += 1
        except BaseException:
            await session.abort()
            raise
        return await session.finish()
