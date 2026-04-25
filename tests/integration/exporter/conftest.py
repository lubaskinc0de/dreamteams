from collections.abc import AsyncIterator
from typing import cast

import httpx
import pytest
from dishka import AsyncContainer
from faststream.nats import NatsBroker
from faststream.nats.publisher.usecase import LogicPublisher

from dreamteams_common.observability.config import OTelConfig
from dreamteams_exporter.adapters.broker.config import NatsConfig
from dreamteams_exporter.adapters.cache.config import CacheConfig
from dreamteams_exporter.adapters.http.config import DreamteamsApiConfig
from dreamteams_exporter.adapters.storage.config import S3Config
from dreamteams_exporter.application.common.gateway.export_job import ExportJobGateway
from dreamteams_exporter.bootstrap.config.loader import Config as ExporterConfig
from dreamteams_exporter.bootstrap.config.sentry import SentryConfig
from dreamteams_exporter.bootstrap.config.server import ServerConfig
from tests.integration.api_client import ApiClient, APIClientConfig
from tests.integration.containers import RUSTFS_ACCESS_KEY, RUSTFS_SECRET_KEY, RustFsContainer
from tests.integration.exporter.facade import ExporterGateway
from tests.integration.exporter.helpers import AUTH_HEADER_NAME


@pytest.fixture
def exporter_config(
    redis_url: str,
    rustfs: RustFsContainer,
    rustfs_bucket: str,
) -> ExporterConfig:
    """Exporter config wired to the same test infrastructure as the main app."""
    rustfs_endpoint = rustfs.get_endpoint_url()
    return ExporterConfig(
        cache=CacheConfig(url=redis_url, rate_limit_window_seconds=3600, rate_limit_max=10),
        nats=NatsConfig(url="nats://test", stream_name="exporter", process_subject="exporter.jobs.process"),
        s3=S3Config(
            bucket_name=rustfs_bucket,
            endpoint_url=rustfs_endpoint,
            access_key=RUSTFS_ACCESS_KEY,
            secret_key=RUSTFS_SECRET_KEY,
            region="us-east-1",
            public_url=f"{rustfs_endpoint}/{rustfs_bucket}",
        ),
        dreamteams_api=DreamteamsApiConfig(
            base_url="http://dreamteams.test",
            auth_header_name=AUTH_HEADER_NAME,
            timeout_seconds=10.0,
        ),
        server=ServerConfig(host="127.0.0.1", port=0, workers=1),
        otel=OTelConfig(
            endpoint="http://localhost:1",
            service_name="dreamteams-exporter-test",
            sample_ratio=0.0,
            metric_export_interval_ms=3_600_000,
            instrument_sqlalchemy=False,
            enabled=False,
        ),
        sentry=SentryConfig(dsn=None),
    )


@pytest.fixture
def exporter_broker() -> NatsBroker:
    """Bare in-memory NATS broker shared between HTTP app and worker setup."""
    return NatsBroker()


@pytest.fixture
def process_job_publisher(exporter_config: ExporterConfig, exporter_broker: NatsBroker) -> LogicPublisher:
    """Declared process-job publisher — must be created before TestNatsBroker starts."""
    return exporter_broker.publisher(
        exporter_config.nats.process_subject,
        stream=exporter_config.nats.stream_name,
    )


@pytest.fixture
async def exporter_container(exporter_app: object) -> AsyncContainer:
    """Dishka container belonging to the exporter test app."""
    return cast("AsyncContainer", exporter_app.state.dishka_container)  # type: ignore[attr-defined]


@pytest.fixture
async def exporter_client(
    exporter_app: object,
    exporter_config: ExporterConfig,
) -> AsyncIterator[ApiClient]:
    """HTTP client speaking to the in-process exporter API."""
    transport = httpx.ASGITransport(app=exporter_app, raise_app_exceptions=False)  # type: ignore[arg-type]
    async with httpx.AsyncClient(transport=transport, base_url="http://exporter.test") as session:
        yield ApiClient(
            session=session,
            config=APIClientConfig(
                auth_user_id_header=exporter_config.dreamteams_api.auth_header_name,
                auth_user_email_header="X-Auth-User-Email",
                access_token_header="X-Access-Token",
            ),
        )


@pytest.fixture
async def export_job_gateway(exporter_container: AsyncContainer) -> ExportJobGateway:
    """Exporter job gateway resolved from the exporter Dishka container."""
    return await exporter_container.get(ExportJobGateway)


@pytest.fixture
async def exporter_gateway(
    exporter_client: ApiClient,
    export_job_gateway: ExportJobGateway,
    http_session: httpx.AsyncClient,
    process_job_publisher: LogicPublisher,
    exporter_config: ExporterConfig,
) -> ExporterGateway:
    """Exporter integration-test facade."""
    return ExporterGateway(
        client=exporter_client,
        job_gateway=export_job_gateway,
        http_session=http_session,
        publisher=process_job_publisher,
        auth_header_name=exporter_config.dreamteams_api.auth_header_name,
    )
