from collections.abc import AsyncIterator

from aiohttp import ClientSession
from dishka import Provider, Scope, provide, provide_all
from faststream.nats import NatsBroker
from faststream.nats.publisher.usecase import LogicPublisher
from redis.asyncio import Redis

from dreamteams_common.clock import Clock, SystemClock
from dreamteams_exporter.adapters.broker.config import NatsConfig
from dreamteams_exporter.adapters.cache.config import CacheConfig
from dreamteams_exporter.adapters.cache.redis_export_job_gateway import RedisExportJobGateway
from dreamteams_exporter.adapters.cache.redis_rate_limiter import RedisExportRateLimiter
from dreamteams_exporter.adapters.event_bus import InMemoryEventBus
from dreamteams_exporter.adapters.event_handler_registry import EventHandlersRegistry
from dreamteams_exporter.adapters.http.client import DreamTeamsApiClient
from dreamteams_exporter.adapters.http.config import DreamteamsApiConfig
from dreamteams_exporter.adapters.http.session import aiohttp_session
from dreamteams_exporter.adapters.http.user_gateway import HttpUserGateway
from dreamteams_exporter.adapters.metrics import (
    ExportJobCreatedMetricsEventHandler,
    ExportJobEnqueuedMetricsEventHandler,
    ExportJobFailedMetricsEventHandler,
    ExportJobSucceededMetricsEventHandler,
)
from dreamteams_exporter.adapters.storage.config import S3Config
from dreamteams_exporter.adapters.storage.s3_spreadsheet_exporter import CsvS3SpreadsheetExporter
from dreamteams_exporter.application.common.event_bus import EventBus
from dreamteams_exporter.application.common.gateway.export_job import ExportJobGateway
from dreamteams_exporter.application.common.rate_limiter import ExportRateLimiter
from dreamteams_exporter.application.common.spreadsheet_exporter import SpreadsheetExporter


class AdapterProvider(Provider):
    """Wires every long-lived adapter used by the exporter entry points."""

    clock = provide(SystemClock, scope=Scope.APP, provides=Clock)
    rate_limiter = provide(RedisExportRateLimiter, scope=Scope.APP, provides=ExportRateLimiter)
    dreamteams_api_client = provide(DreamTeamsApiClient, scope=Scope.APP)
    user_gateway = provide(HttpUserGateway, scope=Scope.APP)
    export_job_gateway = provide(RedisExportJobGateway, scope=Scope.APP, provides=ExportJobGateway)
    metrics_handlers = provide_all(
        ExportJobCreatedMetricsEventHandler,
        ExportJobEnqueuedMetricsEventHandler,
        ExportJobSucceededMetricsEventHandler,
        ExportJobFailedMetricsEventHandler,
        scope=Scope.APP,
    )
    event_handlers_registry = provide(EventHandlersRegistry, scope=Scope.REQUEST)

    @provide(scope=Scope.REQUEST, provides=EventBus)
    def get_event_bus(self, handlers: EventHandlersRegistry) -> InMemoryEventBus:
        """Provide the in-memory event bus with adapter-side exporter handlers."""
        return InMemoryEventBus(handlers.as_mapping())

    @provide(scope=Scope.APP)
    async def get_spreadsheet_exporter(self, config: S3Config) -> AsyncIterator[SpreadsheetExporter]:
        """Ensures the S3 bucket exists on startup, then yields the exporter for the process lifetime."""
        exporter = CsvS3SpreadsheetExporter(config)
        await exporter.ensure_bucket()
        yield exporter

    @provide(scope=Scope.APP)
    async def get_redis(self, config: CacheConfig) -> AsyncIterator[Redis]:
        """Single Redis client for the process."""
        client: Redis = Redis.from_url(config.url, decode_responses=True)
        try:
            yield client
        finally:
            await client.aclose()

    @provide(scope=Scope.APP)
    async def get_aiohttp_session(self, config: DreamteamsApiConfig) -> AsyncIterator[ClientSession]:
        """Single aiohttp client session shared by every outbound gateway."""
        async with aiohttp_session(config) as session:
            yield session

    @provide(scope=Scope.APP)
    async def get_nats_broker(self, config: NatsConfig) -> AsyncIterator[NatsBroker]:
        """
        Broker connection used by the HTTP container to publish ``exporter.jobs.process`` events.

        In the worker container, FastStream manages its own broker lifecycle via ``app.run()``;
        this provider is only meaningful for the HTTP path.
        """
        broker = NatsBroker(config.url)
        await broker.connect()
        try:
            yield broker
        finally:
            await broker.stop()

    @provide(scope=Scope.APP)
    def get_process_job_publisher(self, broker: NatsBroker, config: NatsConfig) -> LogicPublisher:
        """Publisher used by the HTTP path to enqueue process-job messages."""
        return broker.publisher(config.process_subject, stream=config.stream_name)
