import json
from typing import override

from adaptix import Retort
from redis.asyncio import Redis

from dreamteams_exporter.application.common.dto.export_job import ExportJobModel
from dreamteams_exporter.application.common.gateway.export_job import ExportJobGateway
from dreamteams_exporter.application.common.spreadsheet_exporter import SpreadsheetExporter
from dreamteams_exporter.application.errors.job import JobNotFoundError
from dreamteams_exporter.entities.common.identifiers import ExportJobId
from dreamteams_exporter.entities.export_job.entity import ExportApplicationsJob

_JOB_KEY_PREFIX = "exporter:job:"
_retort = Retort()


def _job_key(job_id: ExportJobId) -> str:
    return f"{_JOB_KEY_PREFIX}{job_id}"


def _dump_job(job: ExportApplicationsJob) -> str:
    return json.dumps(_retort.dump(job, ExportApplicationsJob), separators=(",", ":"))


def _load_job(payload: str | bytes) -> ExportApplicationsJob:
    raw_payload = payload.decode() if isinstance(payload, bytes) else payload
    return _retort.load(json.loads(raw_payload), ExportApplicationsJob)


async def _to_model(job: ExportApplicationsJob, spreadsheet_exporter: SpreadsheetExporter) -> ExportJobModel:
    file_url = await spreadsheet_exporter.get_download_url(job.file_key) if job.file_key is not None else None
    return ExportJobModel(
        id=job.id,
        user_id=job.user_id,
        competition_id=job.competition_id,
        application_status=job.application_status,
        status_kind=job.status.kind.value,
        status_reason=job.status.reason,
        file_url=file_url,
        created_at=job.created_at,
        finished_at=job.finished_at,
    )


class RedisExportJobGateway(ExportJobGateway):
    """Redis-backed export-job persistence using one JSON document per job."""

    def __init__(self, redis: Redis, spreadsheet_exporter: SpreadsheetExporter) -> None:
        self._redis = redis
        self._spreadsheet_exporter = spreadsheet_exporter

    @override
    async def create(self, job: ExportApplicationsJob) -> None:
        await self._redis.set(_job_key(job.id), _dump_job(job), nx=True)

    @override
    async def get(self, job_id: ExportJobId) -> ExportApplicationsJob | None:
        payload = await self._redis.get(_job_key(job_id))
        if payload is None:
            return None
        return _load_job(payload)

    @override
    async def read(self, job_id: ExportJobId) -> ExportJobModel | None:
        job = await self.get(job_id)
        if job is None:
            return None
        return await _to_model(job, self._spreadsheet_exporter)

    @override
    async def save(self, job: ExportApplicationsJob) -> None:
        saved = await self._redis.set(_job_key(job.id), _dump_job(job), xx=True)
        if not saved:
            raise JobNotFoundError
