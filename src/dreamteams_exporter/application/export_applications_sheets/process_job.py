import json
from dataclasses import dataclass
from time import monotonic
from typing import Any

import structlog
from opentelemetry import trace

from dreamteams_common.clock import Clock
from dreamteams_common.errors import AppError
from dreamteams_common.interactor import interactor
from dreamteams_common.logger import Logger
from dreamteams_exporter.application.common.dto.export_row import EXPORT_BASE_HEADERS, ExportRow
from dreamteams_exporter.application.common.event_bus import EventBus
from dreamteams_exporter.application.common.events import ExportJobFailed, ExportJobSucceeded
from dreamteams_exporter.application.common.gateway.application_form import ApplicationFormGateway
from dreamteams_exporter.application.common.gateway.applications import ApplicationsGateway
from dreamteams_exporter.application.common.gateway.export_job import ExportJobGateway
from dreamteams_exporter.application.common.idp import IdProvider
from dreamteams_exporter.application.common.rate_limiter import ExportRateLimiter
from dreamteams_exporter.application.common.spreadsheet_exporter import SpreadsheetExporter
from dreamteams_exporter.application.errors.job import JobNotFoundError
from dreamteams_exporter.entities.application.entity import Application
from dreamteams_exporter.entities.application_form.entity import ApplicationForm
from dreamteams_exporter.entities.common.identifiers import ExportJobId
from dreamteams_exporter.entities.common.vo.participant_contact import ParticipantContact
from dreamteams_exporter.entities.export_job.entity import ExportApplicationsJob

logger: Logger = structlog.get_logger(__name__)

_PAGE_SIZE = 100


@dataclass(slots=True, kw_only=True, frozen=True)
class ProcessExportJobInput:
    """Payload accepted by the process-job interactor."""

    job_id: ExportJobId


@dataclass(slots=True, kw_only=True, frozen=True)
class ExportStreamResult:
    """Result of streaming one export job to spreadsheet storage."""

    file_key: str
    rows_count: int
    pages_count: int


def _format_contacts(contacts: list[ParticipantContact]) -> str:
    return ", ".join(f"{c.title}: {c.value}" for c in contacts)


def _format_form_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        return ", ".join(str(item) for item in value)
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return str(value)


def _form_headers(form: ApplicationForm | None) -> list[str]:
    if form is None:
        return []
    return [field.name for field in form.fields]


def _to_export_row(application: Application, form: ApplicationForm | None) -> ExportRow:
    """Project an Application entity into the flattened cells exported to the sheet."""
    form_data = application.form_data or {}
    form_cells = [_format_form_value(form_data.get(field.name)) for field in form.fields] if form is not None else []
    return [
        application.participant.full_name,
        application.competition_name,
        application.status.value,
        application.track,
        str(application.participant.age),
        application.participant.participant_type,
        _format_contacts(application.participant.contacts),
        *form_cells,
        application.created_at.strftime("%d.%m.%Y %H:%M"),
    ]


@interactor
class ExportApplicationsToSheets:
    """Interactor that builds the spreadsheet export for a previously-created job and persists it."""

    idp: IdProvider
    job_gateway: ExportJobGateway
    application_form_gateway: ApplicationFormGateway
    applications_gateway: ApplicationsGateway
    rate_limiter: ExportRateLimiter
    spreadsheet_exporter: SpreadsheetExporter
    event_bus: EventBus
    clock: Clock

    async def execute(self, data: ProcessExportJobInput) -> None:
        """Build the spreadsheet for the given job, stream it out, and mark the job succeeded or failed."""
        user = await self.idp.get_user()
        job = await self.job_gateway.get(data.job_id)
        if job is None:
            raise JobNotFoundError

        started_at = monotonic()
        span = trace.get_current_span()
        span.set_attribute("dreamteams_exporter.export_job.id", str(job.id))
        span.set_attribute("dreamteams_exporter.export_job.competition_id", str(job.competition_id))
        span.set_attribute(
            "dreamteams_exporter.export_job.application_status",
            job.application_status.value if job.application_status is not None else "all",
        )

        try:
            await self.rate_limiter.check_and_record(user.user_id)
            result = await self._stream_to_spreadsheet(job)
        except AppError as exc:
            logger.warning("Export failed with domain error", job_id=job.id, code=exc.code)
            job.mark_failed(str(exc), self.clock)
            await self.job_gateway.save(job)

            duration_seconds = monotonic() - started_at
            span.set_attribute("dreamteams_exporter.export_job.outcome", "domain_error")
            span.set_attribute("dreamteams_exporter.export_job.duration_seconds", duration_seconds)

            await self.event_bus.publish(
                ExportJobFailed(
                    application_status=job.application_status,
                    duration_seconds=duration_seconds,
                    outcome="domain_error",
                ),
            )
            raise
        except Exception as exc:
            logger.exception("Export failed with unexpected error", job_id=job.id)
            job.mark_failed(f"unexpected: {type(exc).__name__}", self.clock)
            await self.job_gateway.save(job)

            duration_seconds = monotonic() - started_at
            span.set_attribute("dreamteams_exporter.export_job.outcome", "unexpected_error")
            span.set_attribute("dreamteams_exporter.export_job.duration_seconds", duration_seconds)

            await self.event_bus.publish(
                ExportJobFailed(
                    application_status=job.application_status,
                    duration_seconds=duration_seconds,
                    outcome="unexpected_error",
                ),
            )
            raise

        job.mark_success(result.file_key, self.clock)
        await self.job_gateway.save(job)

        duration_seconds = monotonic() - started_at
        span.set_attribute("dreamteams_exporter.export_job.outcome", "success")
        span.set_attribute("dreamteams_exporter.export_job.duration_seconds", duration_seconds)
        span.set_attribute("dreamteams_exporter.export_job.rows_count", result.rows_count)
        span.set_attribute("dreamteams_exporter.export_job.pages_count", result.pages_count)

        await self.event_bus.publish(
            ExportJobSucceeded(
                application_status=job.application_status,
                duration_seconds=duration_seconds,
                rows_count=result.rows_count,
                pages_count=result.pages_count,
            ),
        )
        logger.info("Export finished", job_id=job.id, rows_count=result.rows_count, pages_count=result.pages_count)

    async def _stream_to_spreadsheet(self, job: ExportApplicationsJob) -> ExportStreamResult:
        form = await self.application_form_gateway.get_by_competition_id(job.competition_id)
        session = await self.spreadsheet_exporter.start(
            key=f"exports/{job.id}.csv",
            headers=[
                *EXPORT_BASE_HEADERS[:7],
                *_form_headers(form),
                *EXPORT_BASE_HEADERS[7:],
            ],
        )
        try:
            page = 1
            rows_count = 0
            pages_count = 0
            while True:
                batch = await self.applications_gateway.list(
                    competition_id=job.competition_id,
                    status=job.application_status,
                    page=page,
                    page_size=_PAGE_SIZE,
                )
                rows_count += len(batch.items)
                pages_count += 1
                await session.write_rows(_to_export_row(app, form) for app in batch.items)

                if not batch.has_next:
                    break
                page += 1
        except BaseException:
            await session.abort()
            raise

        file_key = await session.finish()
        return ExportStreamResult(file_key=file_key, rows_count=rows_count, pages_count=pages_count)
