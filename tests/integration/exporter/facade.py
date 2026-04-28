import asyncio
import csv
import io
from dataclasses import dataclass

import httpx
from adaptix import Retort
from faststream.nats.publisher.usecase import LogicPublisher

from dreamteams_common.clock import SystemClock
from dreamteams_exporter.application.common.dto.export_job import ExportJobModel
from dreamteams_exporter.application.common.gateway.export_job import ExportJobGateway
from dreamteams_exporter.application.export_applications_sheets.create_job import CreateExportJobInput
from dreamteams_exporter.entities.common.identifiers import CompetitionId, ExportJobId, UserId
from dreamteams_exporter.entities.common.vo.application_status import ApplicationStatus
from dreamteams_exporter.entities.export_job.factory import export_job_factory
from tests.integration.api_client import ApiClient, APIResponse

TERMINAL_STATUSES = {"success", "failed"}
HTTP_OK = 200

_retort = Retort()


@dataclass(slots=True)
class ExporterGateway:
    """Facade for exporter-specific integration-test operations."""

    client: ApiClient
    job_gateway: ExportJobGateway
    http_session: httpx.AsyncClient
    publisher: LogicPublisher
    auth_header_name: str

    async def create(
        self,
        *,
        auth_user_id: str,
        competition_id: CompetitionId,
        application_status: ApplicationStatus | None = None,
    ) -> ExportJobModel:
        """Create an export job through the HTTP API and return its persisted model."""
        with self.client.authenticate(auth_user_id=auth_user_id):
            created = (
                (
                    await self.client.create_export(
                        _retort.dump(
                            CreateExportJobInput(
                                competition_id=competition_id,
                                application_status=application_status,
                            ),
                        ),
                    )
                )
                .assert_status(200)
                .ensure_content()
            )

        model = await self.job_gateway.read(created.job_id)
        if model is None:
            msg = f"Export job {created.job_id} was not persisted"
            raise AssertionError(msg)
        return model

    async def read(
        self,
        *,
        auth_user_id: str,
        job_id: ExportJobId,
    ) -> APIResponse[ExportJobModel]:
        """Read an export job through the HTTP API as a given user."""
        with self.client.authenticate(auth_user_id=auth_user_id):
            return await self.client.read_export(job_id)

    async def seed(
        self,
        *,
        user_id: UserId,
        competition_id: CompetitionId,
        application_status: ApplicationStatus | None = ApplicationStatus.PENDING,
        finished_status: str | None = None,
        file_url: str = "http://storage.example.com/exports/file.csv",
        failed_reason: str = "seeded failure",
    ) -> ExportJobModel:
        """Persist an exporter job through the real exporter job gateway."""
        clock = SystemClock()
        job = export_job_factory(
            user_id=user_id,
            competition_id=competition_id,
            application_status=application_status,
            clock=clock,
        )

        if finished_status == "success":
            job.mark_success(file_url, clock)
        elif finished_status == "failed":
            job.mark_failed(failed_reason, clock)
        await self.job_gateway.create(job)

        model = await self.job_gateway.read(job.id)
        if model is None:
            msg = f"Export job {job.id} was not persisted"
            raise AssertionError(msg)
        return model

    async def publish_process(self, *, job_id: ExportJobId, auth_user_id: str) -> None:
        """Publish a process-job message through the test broker."""
        await self.publisher.publish(
            {"job_id": str(job_id)},
            headers={self.auth_header_name: auth_user_id},
        )

    async def wait_http_job(
        self,
        *,
        job_id: ExportJobId,
        auth_user_id: str,
        status_kind: str | None = None,
        timeout_seconds: float = 10.0,
    ) -> ExportJobModel:
        """Wait until the HTTP API exposes the expected job state."""
        deadline = asyncio.get_running_loop().time() + timeout_seconds
        last_model: ExportJobModel | None = None

        while asyncio.get_running_loop().time() < deadline:
            with self.client.authenticate(auth_user_id=auth_user_id):
                response = await self.client.read_export(job_id)
            if response.status == HTTP_OK:
                last_model = response.ensure_content()
                if status_kind is not None and last_model.status_kind == status_kind:
                    return last_model
                if status_kind is None and last_model.status_kind in TERMINAL_STATUSES:
                    return last_model
            await asyncio.sleep(0.1)

        msg = f"Export job {job_id} did not reach {status_kind or 'a terminal state'}; last model = {last_model}"
        raise TimeoutError(msg)

    async def fetch_csv_rows(self, file_url: str) -> list[dict[str, str]]:
        """Fetch an exported CSV file and return rows keyed by header."""
        text = await self.fetch_csv_text(file_url)
        return list(csv.DictReader(io.StringIO(text)))

    async def fetch_csv_text(self, file_url: str) -> str:
        """Fetch an exported CSV file and decode the UTF-8 BOM if present."""
        response = await self.http_session.get(file_url)
        response.raise_for_status()
        return response.content.decode("utf-8-sig")

    async def fetch_public_file_status(self, file_url: str) -> int:
        """Fetch a public export URL and return its HTTP status."""
        response = await self.http_session.get(file_url)
        return response.status_code
