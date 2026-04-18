from collections.abc import AsyncIterator

from dishka import AnyOf, Provider, Scope, WithParents, provide, provide_all
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from dreamteams.adapters.argon2_password_hasher import Argon2PasswordHasher
from dreamteams.adapters.auth.auth_provider import SimpleAuthProvider
from dreamteams.adapters.auth.idp.auth_user import WebAuthUserIdProvider
from dreamteams.adapters.auth.idp.user import IdProviderImpl
from dreamteams.adapters.avatar_storage import S3AvatarStorage, S3Config
from dreamteams.adapters.cache.config import CacheConfig
from dreamteams.adapters.cache.redis_auth_user_cache import RedisAuthUserCache
from dreamteams.adapters.clock import SystemClock
from dreamteams.adapters.db.config import DbConfig
from dreamteams.adapters.db.gateway.application import SAApplicationGateway
from dreamteams.adapters.db.gateway.application_form import SAApplicationFormGateway
from dreamteams.adapters.db.gateway.auth_user import SAAuthUserGateway
from dreamteams.adapters.db.gateway.competition import SACompetitionGateway
from dreamteams.adapters.db.gateway.organizer import SAOrganizerGateway
from dreamteams.adapters.db.gateway.organizer_invite import SAOrganizerInviteGateway
from dreamteams.adapters.db.gateway.participant import SAParticipantGateway
from dreamteams.adapters.db.gateway.user import SAUserGateway
from dreamteams.adapters.db.pool_metrics import register_pool_metrics
from dreamteams.application.common.uow import UoW
from dreamteams.bootstrap.observability import OTelConfig
from dreamteams.presentation.fast_api.config import ServerConfig


class AdapterProvider(Provider):
    """Dishka provider that registers all adapter implementations."""

    id_providers = provide_all(
        WithParents[WebAuthUserIdProvider],
        WithParents[IdProviderImpl],
        scope=Scope.REQUEST,
    )
    gateways = provide_all(
        WithParents[SAUserGateway],
        WithParents[SAAuthUserGateway],
        WithParents[SAOrganizerGateway],
        WithParents[SAParticipantGateway],
        WithParents[SACompetitionGateway],
        WithParents[SAOrganizerInviteGateway],
        WithParents[SAApplicationFormGateway],
        WithParents[SAApplicationGateway],
        scope=Scope.REQUEST,
    )
    auth_provider = provide(WithParents[SimpleAuthProvider], scope=Scope.REQUEST)
    clock = provide(WithParents[SystemClock], scope=Scope.APP)
    password_hasher = provide(WithParents[Argon2PasswordHasher], scope=Scope.APP)
    auth_user_cache = provide(WithParents[RedisAuthUserCache], scope=Scope.APP)

    @provide(scope=Scope.APP)
    async def get_redis(self, config: CacheConfig) -> AsyncIterator[Redis]:
        """Shared async Redis client; used by cache adapters."""
        client: Redis = Redis.from_url(config.url, decode_responses=False)
        try:
            yield client
        finally:
            await client.aclose()

    @provide(scope=Scope.APP)
    async def get_avatar_storage(self, config: S3Config) -> WithParents[S3AvatarStorage]:
        """Get S3 avatar storage."""
        storage = S3AvatarStorage(config)
        await storage.ensure_bucket_exists()
        return storage

    @provide(scope=Scope.APP)
    async def get_engine(
        self,
        config: DbConfig,
        server_config: ServerConfig,
        otel_config: OTelConfig,
    ) -> AsyncIterator[AsyncEngine]:
        """Provides SQLAlchemy async engine instance with proper lifecycle management."""
        workers = max(1, server_config.workers)
        pool_size = max(1, config.max_total_pool_size // workers)
        max_overflow = max(0, config.max_total_overflow // workers)
        engine = create_async_engine(
            config.connection_url,
            future=True,
            # Per-worker pool derived from TOML ``db.max_total_pool_size`` // ``server.workers``.
            # Total client conns across all workers = max_total_pool_size + max_total_overflow,
            # which must stay below pgbouncer's DEFAULT_POOL_SIZE.
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_timeout=30,
            pool_recycle=1800,
            # statement caching works under pgbouncer transaction pooling when the bouncer
            # has MAX_PREPARED_STATEMENTS > 0 (>=1.21); asyncpg defaults (large prepared
            # cache) are then safe and dramatically reduce parse/plan overhead.
        )
        register_pool_metrics(engine)
        if otel_config.instrument_sqlalchemy:
            SQLAlchemyInstrumentor().instrument(
                engine=engine.sync_engine,
                enable_commenter=True,
            )
        yield engine
        if otel_config.instrument_sqlalchemy:
            SQLAlchemyInstrumentor().uninstrument()
        await engine.dispose()

    @provide(scope=Scope.APP)
    async def get_async_sessionmaker(
        self,
        engine: AsyncEngine,
    ) -> async_sessionmaker[AsyncSession]:
        """Provides SQLAlchemy async session factory configured for the application."""
        session_factory = async_sessionmaker(
            engine,
            expire_on_commit=False,
            class_=AsyncSession,
        )
        return session_factory

    @provide(scope=Scope.REQUEST)
    async def get_async_session(
        self,
        session_factory: async_sessionmaker[AsyncSession],
    ) -> AsyncIterator[AnyOf[AsyncSession, UoW]]:
        """Provides a request-scoped database session that also implements the UoW protocol."""
        async with session_factory() as session:
            yield session
