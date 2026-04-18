from collections.abc import AsyncIterator

from dishka import AnyOf, Provider, Scope, WithParents, provide, provide_all
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from dreamteams.adapters.argon2_password_hasher import Argon2PasswordHasher
from dreamteams.adapters.auth.auth_provider import SimpleAuthProvider
from dreamteams.adapters.auth.idp.auth_user import WebAuthUserIdProvider
from dreamteams.adapters.auth.idp.user import IdProviderImpl
from dreamteams.adapters.avatar_storage import S3AvatarStorage, S3Config
from dreamteams.adapters.clock import SystemClock
from dreamteams.adapters.db.config import DbConfig
from dreamteams.adapters.db.gateway.application import SAApplicationGateway
from dreamteams.adapters.db.gateway.application_form import SAApplicationFormGateway
from dreamteams.adapters.db.gateway.auth_user import SAAuthUserGateway
from dreamteams.adapters.db.gateway.competition import SACompetitionGateway
from dreamteams.adapters.db.gateway.organizer import SAOrganizerGateway
from dreamteams.adapters.db.gateway.organizer_invite import SAOrganizerInviteGateway
from dreamteams.adapters.db.gateway.user import SAUserGateway
from dreamteams.adapters.db.pool_metrics import register_pool_metrics
from dreamteams.application.common.uow import UoW


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
        WithParents[SACompetitionGateway],
        WithParents[SAOrganizerInviteGateway],
        WithParents[SAApplicationFormGateway],
        WithParents[SAApplicationGateway],
        scope=Scope.REQUEST,
    )
    auth_provider = provide(WithParents[SimpleAuthProvider], scope=Scope.REQUEST)
    clock = provide(WithParents[SystemClock], scope=Scope.APP)
    password_hasher = provide(WithParents[Argon2PasswordHasher], scope=Scope.APP)

    @provide(scope=Scope.APP)
    async def get_avatar_storage(self, config: S3Config) -> WithParents[S3AvatarStorage]:
        """Get S3 avatar storage."""
        storage = S3AvatarStorage(config)
        await storage.ensure_bucket_exists()
        return storage

    @provide(scope=Scope.APP)
    async def get_engine(self, config: DbConfig) -> AsyncIterator[AsyncEngine]:
        """Provides SQLAlchemy async engine instance with proper lifecycle management."""
        engine = create_async_engine(
            config.connection_url,
            future=True,
            pool_size=100,
            max_overflow=100,
            pool_timeout=30,
            pool_recycle=1800,
            connect_args={
                "statement_cache_size": 0,
                "prepared_statement_cache_size": 0,
            },
        )
        register_pool_metrics(engine)
        SQLAlchemyInstrumentor().instrument(
            engine=engine.sync_engine,
            enable_commenter=True,
            commenter_options={},
        )
        yield engine
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
