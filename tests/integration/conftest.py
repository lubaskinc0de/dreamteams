import asyncio
import uuid
from collections.abc import AsyncIterator, Iterator
from importlib.resources import files
from importlib.resources.abc import Traversable
from typing import cast

import alembic.command
import httpx
import pytest
import pytest_asyncio
from alembic.config import Config as AlembicConfig
from asgi_lifespan import LifespanManager
from dishka import AsyncContainer
from faker import Faker
from polyfactory.pytest_plugin import register_fixture
from redis.asyncio import Redis
from sqlalchemy import URL, make_url, text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer

import tests.assets
from dreamteams.adapters.auth.idp.auth_user import WebAuthUserIdProviderConfig
from dreamteams.adapters.avatar_storage import S3Config
from dreamteams.adapters.cache.config import CacheConfig
from dreamteams.adapters.db.alembic.config import get_alembic_config_path
from dreamteams.adapters.db.config import DbConfig
from dreamteams.adapters.sentry import SentryConfig
from dreamteams.application.register_user.register_superuser import SuperuserConfig
from dreamteams.bootstrap.config_loader import Config
from dreamteams.bootstrap.fast_api import create_app
from dreamteams.presentation.fast_api.config import ApiConfig, CorsConfig, ServerConfig
from dreamteams_common.clock import Clock, SystemClock
from dreamteams_common.observability.config import OTelConfig
from tests.common.factory.application import SubmitApplicationInputFactory
from tests.common.factory.application_form import ApplicationFormInputFactory
from tests.common.factory.competition import (
    ChangeCompetitionArchiveStatusFormFactory,
    CompetitionFormFactory,
    RescheduleCompetitionFormFactory,
    UpdateCompetitionGeneralInfoFormFactory,
)
from tests.common.factory.organizer import OrganizerFormFactory, UpdateOrganizerFormFactory
from tests.common.factory.participant import ParticipantFormFactory, UpdateParticipantFormFactory
from tests.integration.api_client import ApiClient, APIClientConfig
from tests.integration.containers import RUSTFS_ACCESS_KEY, RUSTFS_SECRET_KEY, RustFsContainer
from tests.integration.helpers.admin_factory import AdminGateway
from tests.integration.helpers.application_factory import ApplicationGateway
from tests.integration.helpers.application_form_factory import ApplicationFormGateway
from tests.integration.helpers.competition_factory import CompetitionGateway
from tests.integration.helpers.facade import Gateway
from tests.integration.helpers.organizer_factory import OrganizerGateway
from tests.integration.helpers.participant_factory import ParticipantGateway
from tests.integration.helpers.tag_factory import TagGateway

SUPERUSER_PW_HASH = "$argon2id$v=19$m=65536,t=3,p=4$WtB09we21GMOQ8kjBOFnrQ$ZU8lTm3cNPhFe90PGfH5sliQvzlbZf6DKztbxNlOl2s"


@pytest.fixture(scope="session")
def postgres() -> Iterator[PostgresContainer]:
    """Postgres testcontainer for the whole worker. The ``template_db`` DB is cloned per test."""
    with PostgresContainer("postgres:18-alpine", dbname="template_db") as pg:
        yield pg


@pytest.fixture(scope="session")
def redis_testcontainer() -> Iterator[RedisContainer]:
    """Redis testcontainer for the whole worker; flushed between tests."""
    with RedisContainer("redis:7.0") as rc:
        yield rc


@pytest.fixture(scope="session")
def rustfs() -> Iterator[RustFsContainer]:
    """RustFS (S3-compatible) testcontainer for the whole worker; shared across tests."""
    with RustFsContainer() as fs:
        yield fs


def _run_migrations_sync(db_url: URL) -> None:
    alembic_path_gen = get_alembic_config_path()
    alembic_path = str(next(alembic_path_gen))
    cfg = AlembicConfig(alembic_path)
    cfg.attributes["db_url"] = db_url
    alembic.command.upgrade(cfg, "head")


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def template_db_url(postgres: PostgresContainer) -> str:
    """Session-wide URL of the already-migrated template database; each test clones off this."""
    sync_url = postgres.get_connection_url()
    async_url_str = sync_url.replace("postgresql+psycopg2", "postgresql+asyncpg")
    async_url = make_url(async_url_str)

    await asyncio.to_thread(_run_migrations_sync, async_url)
    return async_url.render_as_string(hide_password=False)


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def pg_admin_engine(template_db_url: str) -> AsyncIterator[AsyncEngine]:
    """Engine on the ``postgres`` DB with AUTOCOMMIT for CREATE/DROP DATABASE."""
    admin_url = make_url(template_db_url).set(database="postgres")
    engine = create_async_engine(admin_url, isolation_level="AUTOCOMMIT")
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(loop_scope="session")
async def test_db_url(template_db_url: str, pg_admin_engine: AsyncEngine) -> AsyncIterator[str]:
    """Per-test cloned database made via ``CREATE DATABASE ... TEMPLATE template_db``; dropped after."""
    template_url = make_url(template_db_url)
    template_name = cast("str", template_url.database)
    db_name = f"test_{uuid.uuid4().hex}"

    async with pg_admin_engine.connect() as conn:
        await conn.execute(text(f'CREATE DATABASE "{db_name}" TEMPLATE "{template_name}"'))

    yield template_url.set(database=db_name).render_as_string(hide_password=False)

    async with pg_admin_engine.connect() as conn:
        await conn.execute(text(f'DROP DATABASE "{db_name}" WITH (FORCE)'))


@pytest.fixture(scope="session")
def rustfs_bucket() -> str:
    """Single shared bucket name per worker — avatar keys are uuid-namespaced per test."""
    return f"dreamteams-test-{uuid.uuid4().hex[:8]}"


@pytest.fixture
def app_config(
    test_db_url: str,
    redis_url: str,
    rustfs: RustFsContainer,
    rustfs_bucket: str,
) -> Config:
    """Per-test ``Config`` wired to the testcontainer URLs. Never calls ``Config.load()``."""
    db_url = make_url(test_db_url)
    return Config(
        db=DbConfig(
            user=db_url.username or "",
            password=db_url.password or "",
            host=db_url.host or "",
            port=db_url.port or 5432,
            db_name=db_url.database or "",
            max_total_pool_size=5,
            max_total_overflow=5,
        ),
        auth=WebAuthUserIdProviderConfig(
            user_id_header="X-Auth-User",
            user_email_header="X-Auth-User-Email",
            access_token_header="X-Access-Token",
            access_token_alg="RS256",
            allow_unverified_email=True,
        ),
        otel=OTelConfig(
            endpoint="http://localhost:1",
            service_name="dreamteams-test",
            sample_ratio=0.0,
            metric_export_interval_ms=3_600_000,
            instrument_sqlalchemy=False,
            enabled=False,
        ),
        server=ServerConfig(host="localhost", port=0, workers=1),
        cors=CorsConfig(
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        ),
        api=ApiConfig(root_path=""),
        s3=S3Config(
            bucket_name=rustfs_bucket,
            endpoint_url=rustfs.get_endpoint_url(),
            access_key=RUSTFS_ACCESS_KEY,
            secret_key=RUSTFS_SECRET_KEY,
            region="us-east-1",
            public_url=rustfs.get_endpoint_url(),
        ),
        superuser=SuperuserConfig(
            password_hash=SUPERUSER_PW_HASH,
        ),
        sentry=SentryConfig(dsn=None),
        cache=CacheConfig(
            url=redis_url,
            auth_user_ttl_seconds=60,
            auth_user_ttl_jitter_seconds=0,
            blocked_user_ttl_seconds=86400,
            application_form_ttl_seconds=900,
            competition_tags_ttl_seconds=1800,
            competition_read_ttl_seconds=120,
        ),
    )


@pytest.fixture(scope="session")
def redis_url(redis_testcontainer: RedisContainer) -> str:
    """Redis connection URL for the shared testcontainer."""
    host = redis_testcontainer.get_container_host_ip()
    port = redis_testcontainer.get_exposed_port(6379)
    return f"redis://{host}:{port}/0"


@pytest_asyncio.fixture(loop_scope="session")
async def app(app_config: Config) -> AsyncIterator[object]:
    """Per-test FastAPI app with lifespan (Dishka container start/stop) wired in-process."""
    fastapi_app = create_app(app_config)
    async with LifespanManager(fastapi_app):
        yield fastapi_app


@pytest_asyncio.fixture(loop_scope="session")
async def container(app: object) -> AsyncContainer:
    """Dishka AsyncContainer belonging to the per-test app."""
    return cast("AsyncContainer", app.state.dishka_container)  # type: ignore[attr-defined]


@pytest_asyncio.fixture(loop_scope="session")
async def session(container: AsyncContainer) -> AsyncIterator[AsyncSession]:
    """AsyncSession from the app's sessionmaker."""
    async with container() as request_container:
        yield await request_container.get(AsyncSession)


@pytest_asyncio.fixture(loop_scope="session")
async def request_container(container: AsyncContainer) -> AsyncIterator[AsyncContainer]:
    """Request-scoped Dishka container for tests that need to resolve request-scoped services."""
    async with container() as scope:
        yield scope


@pytest_asyncio.fixture(loop_scope="session", autouse=True)
async def _flush_redis(container: AsyncContainer) -> AsyncIterator[None]:
    """Clear the cache after each test."""
    yield
    redis = await container.get(Redis)
    await redis.flushdb()


@pytest_asyncio.fixture(loop_scope="session")
async def api_client(app: object, app_config: Config) -> AsyncIterator[ApiClient]:
    """API client speaking to the in-process FastAPI app via httpx.ASGITransport."""
    transport = httpx.ASGITransport(app=app, raise_app_exceptions=False)  # type: ignore[arg-type]
    async with httpx.AsyncClient(transport=transport, base_url="http://test", follow_redirects=True) as http:
        yield ApiClient(
            session=http,
            config=APIClientConfig(
                auth_user_id_header=app_config.auth.user_id_header,
                auth_user_email_header=app_config.auth.user_email_header,
                access_token_header=app_config.auth.access_token_header,
            ),
        )


@pytest_asyncio.fixture(loop_scope="session")
async def http_session() -> AsyncIterator[httpx.AsyncClient]:
    """Plain httpx client for tests that fetch externally-visible URLs (e.g. avatar public URL)."""
    async with httpx.AsyncClient() as client:
        yield client


@pytest.fixture(scope="session")
def clock() -> Clock:
    """Real clock."""
    return SystemClock()


@pytest.fixture
def assets() -> Traversable:
    """File assets for tests."""
    return files(tests.assets)


# Polyfactory

register_fixture(ApplicationFormInputFactory)
register_fixture(SubmitApplicationInputFactory)
register_fixture(CompetitionFormFactory)
register_fixture(UpdateCompetitionGeneralInfoFormFactory)
register_fixture(RescheduleCompetitionFormFactory)
register_fixture(ChangeCompetitionArchiveStatusFormFactory)
register_fixture(OrganizerFormFactory)
register_fixture(UpdateOrganizerFormFactory)
register_fixture(ParticipantFormFactory)
register_fixture(UpdateParticipantFormFactory)


# Gateway


@pytest.fixture
def admin_gateway(session: AsyncSession, api_client: ApiClient) -> AdminGateway:
    """Gateway for admin user creation and invite issuance."""
    return AdminGateway(session=session, api_client=api_client)


@pytest.fixture
def organizer_gateway(
    api_client: ApiClient,
    organizer_form_factory: OrganizerFormFactory,
    faker: Faker,
) -> OrganizerGateway:
    """Gateway for organizer registration."""
    return OrganizerGateway(api_client=api_client, organizer_form_factory=organizer_form_factory, faker=faker)


@pytest.fixture
def participant_gateway(
    api_client: ApiClient,
    participant_form_factory: ParticipantFormFactory,
    faker: Faker,
) -> ParticipantGateway:
    """Gateway for participant registration."""
    return ParticipantGateway(api_client=api_client, participant_form_factory=participant_form_factory, faker=faker)


@pytest.fixture
def competition_gateway(
    api_client: ApiClient,
    session: AsyncSession,
    competition_form_factory: CompetitionFormFactory,
    container: AsyncContainer,
) -> CompetitionGateway:
    """Gateway for competition creation and state manipulation."""
    return CompetitionGateway(
        api_client=api_client,
        session=session,
        competition_form_factory=competition_form_factory,
        container=container,
    )


@pytest.fixture
def application_gateway(
    api_client: ApiClient,
    submit_application_input_factory: SubmitApplicationInputFactory,
    participant_gateway: ParticipantGateway,
    competition_gateway: CompetitionGateway,
) -> ApplicationGateway:
    """Gateway for application submission and status transitions."""
    return ApplicationGateway(
        api_client=api_client,
        submit_application_input_factory=submit_application_input_factory,
        participant_gateway=participant_gateway,
        competition_gateway=competition_gateway,
    )


@pytest.fixture
def application_form_gateway(
    api_client: ApiClient,
    application_form_input_factory: ApplicationFormInputFactory,
) -> ApplicationFormGateway:
    """Gateway for application form creation and deletion."""
    return ApplicationFormGateway(
        api_client=api_client,
        application_form_input_factory=application_form_input_factory,
    )


@pytest.fixture
def tag_gateway(api_client: ApiClient) -> TagGateway:
    """Gateway for competition tag creation."""
    return TagGateway(api_client=api_client)


@pytest.fixture
def gateway(
    admin_gateway: AdminGateway,
    organizer_gateway: OrganizerGateway,
    participant_gateway: ParticipantGateway,
    competition_gateway: CompetitionGateway,
    application_gateway: ApplicationGateway,
    application_form_gateway: ApplicationFormGateway,
    tag_gateway: TagGateway,
) -> Gateway:
    """Facade providing access to all per-entity gateways."""
    return Gateway(
        admin=admin_gateway,
        organizer=organizer_gateway,
        participant=participant_gateway,
        competition=competition_gateway,
        application=application_gateway,
        application_form=application_form_gateway,
        tags=tag_gateway,
    )
