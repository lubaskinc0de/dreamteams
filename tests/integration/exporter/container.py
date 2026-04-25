from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import override

from dishka import AsyncContainer, BaseScope, Provider, Scope, from_context, make_async_container, provide
from dishka.integrations.fastapi import FastapiProvider
from dishka.integrations.fastapi import setup_dishka as setup_fastapi_dishka
from dishka_faststream import FastStreamProvider
from dishka_faststream import setup_dishka as setup_faststream_dishka
from fastapi import FastAPI
from faststream import FastStream
from faststream.nats import NatsBroker
from faststream.nats.publisher.usecase import LogicPublisher

from dreamteams_common.observability.config import OTelConfig
from dreamteams_exporter.adapters.broker.config import NatsConfig
from dreamteams_exporter.adapters.cache.config import CacheConfig
from dreamteams_exporter.adapters.http.config import DreamteamsApiConfig
from dreamteams_exporter.adapters.http.user_gateway import HttpUserGateway
from dreamteams_exporter.adapters.storage.config import S3Config
from dreamteams_exporter.application.common.event_bus import JobEventBus
from dreamteams_exporter.application.common.gateway.applications import ApplicationsGateway
from dreamteams_exporter.bootstrap.config.loader import Config as ExporterConfig
from dreamteams_exporter.bootstrap.config.sentry import SentryConfig
from dreamteams_exporter.bootstrap.config.server import ServerConfig
from dreamteams_exporter.bootstrap.di.providers.adapter import AdapterProvider
from dreamteams_exporter.bootstrap.di.providers.config import ConfigProvider
from dreamteams_exporter.bootstrap.di.providers.http_auth import HttpAuthProvider
from dreamteams_exporter.bootstrap.di.providers.interactor import InteractorProvider
from dreamteams_exporter.bootstrap.di.providers.message_auth import MessageAuthProvider
from dreamteams_exporter.entities.common.identifiers import ExportJobId
from dreamteams_exporter.presentation.fast_api.error_handlers import include_exception_handlers
from dreamteams_exporter.presentation.fast_api.routers import include_routers
from dreamteams_exporter.presentation.faststream.handlers import include_handlers
from tests.integration.api_client import ApiClient
from tests.integration.exporter.fake_gateways import FakeApplicationsGateway, FakeHttpUserGateway


class NoopJobEventBus(JobEventBus):
    """Worker-container placeholder for interactors that are not used by worker tests."""

    @override
    async def publish_process(self, job_id: ExportJobId) -> None:
        """Do nothing."""


class ExporterTestOverridesProvider(Provider):
    """Single test-only provider appended after defaults to override main-context callers."""

    scope: BaseScope | None = Scope.APP
    api_client = from_context(ApiClient)
    user_gateway = provide(FakeHttpUserGateway, provides=HttpUserGateway)
    applications_gateway = provide(FakeApplicationsGateway, scope=Scope.REQUEST, provides=ApplicationsGateway)


class ExporterHttpBrokerOverridesProvider(Provider):
    """Test-only NATS objects controlled by ``TestNatsBroker``."""

    scope: BaseScope | None = Scope.APP
    broker = from_context(NatsBroker)
    process_job_publisher = from_context(LogicPublisher)


class ExporterWorkerOverridesProvider(Provider):
    """Worker-only dependencies needed for full container validation."""

    scope: BaseScope | None = Scope.REQUEST
    event_bus = provide(NoopJobEventBus, provides=JobEventBus)


def _base_context(config: ExporterConfig) -> dict[type, object]:
    return {
        ExporterConfig: config,
        CacheConfig: config.cache,
        NatsConfig: config.nats,
        S3Config: config.s3,
        DreamteamsApiConfig: config.dreamteams_api,
        ServerConfig: config.server,
        OTelConfig: config.otel,
        SentryConfig: config.sentry,
    }


def make_http_container(
    config: ExporterConfig,
    api_client: ApiClient,
    broker: NatsBroker,
    publisher: LogicPublisher,
) -> AsyncContainer:
    """Build the exporter HTTP container with test overrides appended last."""
    return make_async_container(
        ConfigProvider(),
        FastapiProvider(),
        AdapterProvider(),
        HttpAuthProvider(),
        InteractorProvider(),
        ExporterTestOverridesProvider(),
        ExporterHttpBrokerOverridesProvider(),
        context=_base_context(config) | {ApiClient: api_client, NatsBroker: broker, LogicPublisher: publisher},
    )


def make_worker_container(config: ExporterConfig, api_client: ApiClient) -> AsyncContainer:
    """Build the exporter worker container with test overrides appended last."""
    return make_async_container(
        ConfigProvider(),
        FastStreamProvider(),
        AdapterProvider(),
        MessageAuthProvider(),
        InteractorProvider(),
        ExporterTestOverridesProvider(),
        ExporterWorkerOverridesProvider(),
        context=_base_context(config) | {ApiClient: api_client},
    )


def create_exporter_test_app(
    config: ExporterConfig,
    api_client: ApiClient,
    broker: NatsBroker,
    publisher: LogicPublisher,
) -> FastAPI:
    """Create the exporter test app using the overridden HTTP container."""

    @asynccontextmanager
    async def _lifespan(app: FastAPI) -> AsyncIterator[None]:
        container: AsyncContainer = app.state.dishka_container
        try:
            yield
        finally:
            await container.close()

    app = FastAPI(lifespan=_lifespan)
    container = make_http_container(config, api_client, broker, publisher)
    setup_fastapi_dishka(container=container, app=app)
    include_routers(app)
    include_exception_handlers(app)
    return app


def setup_exporter_test_worker(config: ExporterConfig, api_client: ApiClient, broker: NatsBroker) -> FastStream:
    """Attach exporter worker handlers and DI to an existing broker."""
    include_handlers(broker)
    app = FastStream(broker)
    container = make_worker_container(config, api_client)
    setup_faststream_dishka(container=container, app=app, auto_inject=False)
    return app
