import json
from typing import override

from adaptix import Retort
from adaptix.conversion import impl_converter, link_function
from redis.asyncio import Redis

from dreamteams_exporter.application.common.dto.export_job import ExportJobModel
from dreamteams_exporter.application.common.gateway.export_job import ExportJobGateway
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


@impl_converter(
    recipe=[
        link_function(lambda job: job.status.kind.value, "status_kind"),
        link_function(lambda job: job.status.reason, "status_reason"),
    ],
)
def _to_model(job: ExportApplicationsJob) -> ExportJobModel: ...


class RedisExportJobGateway(ExportJobGateway):
    """Redis-backed export-job persistence using one JSON document per job."""

    def __init__(self, redis: Redis) -> None:
        self._redis = redis

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
        return _to_model(job)

    @override
    async def save(self, job: ExportApplicationsJob) -> None:
        saved = await self._redis.set(_job_key(job.id), _dump_job(job), xx=True)
        if not saved:
            raise JobNotFoundError
