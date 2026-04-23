from collections.abc import AsyncIterator

from aiohttp import ClientSession
from dishka import AnyOf, Provider, Scope, provide
from faststream.nats import NatsBroker
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from dreamteams_common.clock import Clock, SystemClock
from dreamteams_common.uow import UoW
from dreamteams_exporter.adapters.broker.config import NatsConfig
from dreamteams_exporter.adapters.cache.config import CacheConfig
from dreamteams_exporter.adapters.cache.redis_rate_limiter import RedisExportRateLimiter
from dreamteams_exporter.adapters.db.config import DbConfig
from dreamteams_exporter.adapters.db.gateway.export_job import SAExportJobGateway
from dreamteams_exporter.adapters.http.config import DreamteamsApiConfig
from dreamteams_exporter.adapters.http.session import aiohttp_session
from dreamteams_exporter.adapters.http.user_gateway import HttpUserGateway
from dreamteams_exporter.adapters.storage.s3_spreadsheet_exporter import CsvS3SpreadsheetExporter
from dreamteams_exporter.application.common.gateway.export_job import ExportJobGateway
from dreamteams_exporter.application.common.rate_limiter import ExportRateLimiter
from dreamteams_exporter.application.common.spreadsheet_exporter import SpreadsheetExporter


class AdapterProvider(Provider):
    """Wires every long-lived adapter plus the per-request DB / gateway instances shared by both entry points."""

    clock = provide(SystemClock, scope=Scope.APP, provides=Clock)
    rate_limiter = provide(RedisExportRateLimiter, scope=Scope.APP, provides=ExportRateLimiter)
    user_gateway = provide(HttpUserGateway, scope=Scope.APP)
    export_job_gateway = provide(SAExportJobGateway, scope=Scope.REQUEST, provides=ExportJobGateway)
    spreadsheet_exporter = provide(CsvS3SpreadsheetExporter, scope=Scope.APP, provides=SpreadsheetExporter)

    @provide(scope=Scope.APP)
    async def get_engine(self, config: DbConfig) -> AsyncIterator[AsyncEngine]:
        """Single async SQLAlchemy engine for the process."""
        engine = create_async_engine(
            config.connection_url,
            pool_size=config.pool_size,
            max_overflow=config.max_overflow,
            pool_timeout=30,
            pool_recycle=1800,
        )
        try:
            yield engine
        finally:
            await engine.dispose()

    @provide(scope=Scope.APP)
    def get_session_maker(self, engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
        """Shared session factory used to produce per-request DB sessions."""
        return async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    @provide(scope=Scope.REQUEST)
    async def get_session(
        self,
        maker: async_sessionmaker[AsyncSession],
    ) -> AsyncIterator[AnyOf[AsyncSession, UoW]]:
        """Opens one DB session per request; also satisfies the application-level UoW protocol."""
        async with maker() as session:
            yield session

    @provide(scope=Scope.APP)
    async def get_redis(self, config: CacheConfig) -> AsyncIterator[Redis]:
        """Single Redis client for the process."""
        client: Redis = Redis.from_url(config.url, decode_responses=False)
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
        """Broker connection used by the HTTP container to publish ``exporter.jobs.process`` events.

        In the worker container, FastStream manages its own broker lifecycle via ``app.run()``;
        this provider is only meaningful for the HTTP path.
        """
        broker = NatsBroker(config.url)
        await broker.connect()
        try:
            yield broker
        finally:
            await broker.stop()
