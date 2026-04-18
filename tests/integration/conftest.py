import os
from collections.abc import AsyncIterable, AsyncIterator
from importlib.resources import files
from importlib.resources.abc import Traversable

import aiohttp
import jwt
import pytest
from aiohttp import ClientSession
from dishka import AsyncContainer
from faker import Faker
from polyfactory.pytest_plugin import register_fixture
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

import tests.assets
from dreamteams.adapters.clock import SystemClock
from dreamteams.bootstrap.config.loader import Config
from dreamteams.bootstrap.di.container import get_async_container
from dreamteams.entities.common.clock import Clock
from tests.common.factory.application import SubmitApplicationInputFactory
from tests.common.factory.application_form import ApplicationFormInputFactory
from tests.common.factory.competition import CompetitionFormFactory, UpdateCompetitionFormFactory
from tests.common.factory.organizer import OrganizerFormFactory, UpdateOrganizerFormFactory
from tests.common.factory.participant import ParticipantFormFactory, UpdateParticipantFormFactory
from tests.integration.api_client import ApiClient, APIClientConfig
from tests.integration.helpers.admin_factory import AdminGateway
from tests.integration.helpers.application_factory import ApplicationGateway
from tests.integration.helpers.application_form_factory import ApplicationFormGateway
from tests.integration.helpers.competition_factory import CompetitionGateway
from tests.integration.helpers.facade import Gateway
from tests.integration.helpers.organizer_factory import OrganizerGateway
from tests.integration.helpers.participant_factory import ParticipantGateway

# This is a fake private key used only to sign fake access token for tests
DUMMY_PRIVATE_KEY = """
-----BEGIN PRIVATE KEY-----
MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDEGaNRi4y3Aneo
kMONcleALP0h2SPEr4Wqj0Bzu3/VEQfhcuMKtWqQenx/wZ1kYlr1NAZUYFxP0VE6
pqlt6x9NGzgaUyp8x/S5jVPjxrcMsq+N+zwES6zrMpTbjJgA6eWlZ50amAgwtVvP
/aUUll6SckDCWpq51Xu/tmMm/uTdPaT/loBVoEfluqLLq4qcqROwnqtOZs/0aTFx
w76tOqsBl+QtaRCoU5XRHgS+Mf0KuMh+mktelDsTEDCyu4cDn5viTQ8C7b5oChbn
lSaPq52aQ3tsrp/3HixW7E2y3d58tIUV+X6/5drdf+QgysNELNO6H/0n+4aXc6DM
MqspZs2DAgMBAAECggEAEYyd0glkEWi2Hq694WWvMPhVuva8vbhbhPUG9pR8DyxU
ATgP24B6xe1AQQqptDcdHr6GJnztJfN8inwpw318MqFR9wEkV0BpxUVBkavR69/9
1/341AWVtwKy0acWX1aPR6srIxsh+IHycn2njV0bn418ACitmh3h0jlXTEEZaDcY
0BlE/eda3yRBO1yIyk1LIFqIotQyEm0eJtuQQX6HlWbGsuBRjCKAI5qhVuxMmVEa
YZVag+Ko0IKjDQxtIH1kLsadMX6/G6p8KO4RZgwsDk7eyR0ISvuCsDb2H2SZDGg6
Zt1uAmxgWTF1RqypAaq/tJN4VXrtI3k61uvo0HwiAQKBgQD0nLUnn9hKR40gF6oN
x+XBWB/CrILDnXKNnfzsf/TLC5t8wHp06lo9kNJKcc3AKXlGU0ikvnYJwJYDVeKG
6V+y3vphS8gGRAg2yI/P9wBOUKvioJyfC04/rZ1SiSZpQUHs2jzgErqFKQqXpCzB
yPYULwhxaCfMG9aXQTIaze3SgwKBgQDNOsNxc40H8OL8Xnbla7JeA+tVK8jb/k30
taC17v7a22Nd+Ao4M/+H6ToCQEXhD0RSsWtmO6ys4mlCuH0+N+h++5sjCd1HmJxm
UrDoP0uVXc4F1R0SmSZoMwkg3Co8I7DNb+eINCh2xAybynIb6w1736HJE/h0JbJS
/0sgpJYpAQKBgQDjmJNtpOqoYl7LB3mwjNgXx5j1l3Gr9OlLHz7gBkaMTeaEcsr9
0bfZJNCld7ILJAu1BXTH5HcLp+dsfxLgmG/0jEfHE62vNsm1v3Mf+yCLvb/Qg8R2
rxxFX5LL4tSchp2CdaTCkGp/z6oNYjJKtGNScFiYvGKbJSPLZFvsWML5ZQKBgB/g
J6kAXIBGPssZ1PevMYX+r9eLtGfO6MbASxTW6QiPGLDorJWsJd0zMUpWN0RMfb0m
R1sam6hChjzRsMowHtFSPPdFOfQ71NbjswxvgErTxgML5bcUyG1Yt+s9puWuWXCf
F+QEzeAcdSThXbXOXUrHIja7/lPz4u2XL1EDnzsBAoGBAJOinUr0t3nUEKhKcqJ9
gJWzg5NcCJa53leWAceA2fpttF2GgEYsR6udisqYI+UH1TUaMrujUqGFbNqXqdHo
7QGJZoHc7/RNeQ14u0SDY37QmyzgMt8/4enn6O4IzMML+b6cDi+khx6dc2NEUu+F
6p95hLlC0FKt9LZYt2jHi5O9
-----END PRIVATE KEY-----
"""

# --- Infrastructure ---


@pytest.fixture(scope="session")
def clock() -> Clock:
    """Real clock."""
    return SystemClock()


@pytest.fixture
async def app_config() -> Config:
    """Load and provide app config."""
    return Config.load()


@pytest.fixture
async def container() -> AsyncIterator[AsyncContainer]:
    """Create and provide async DI container for tests."""
    container = get_async_container(Config.load())
    yield container
    await container.close()


@pytest.fixture
async def request_container(container: AsyncContainer) -> AsyncIterator[AsyncContainer]:
    """Provide async request-scoped DI container for tests."""
    async with container() as request_container:
        yield request_container


@pytest.fixture
async def session(container: AsyncContainer) -> AsyncIterator[AsyncSession]:
    """Create and provide database session for tests."""
    async with container() as r:
        yield (await r.get(AsyncSession))


@pytest.fixture(autouse=True)
async def gracefully_teardown(
    session: AsyncSession,
    container: AsyncContainer,
) -> AsyncIterable[None]:
    """Truncate all tables and flush the app's Redis DB after each test.

    The cache is a read-through for ``auth_user_id -> user_id``; leaving entries
    between tests would cause a fresh row with the same ``auth_user_id`` to resolve
    to a stale ``user_id`` and diverge from the DB. Redis client is resolved through
    the same Dishka container the app uses so both point at the same connection.
    """
    yield
    await session.execute(
        text("""
            DO $$
            DECLARE
                tb text;
            BEGIN
                FOR tb IN (
                    SELECT tablename
                    FROM pg_catalog.pg_tables
                    WHERE schemaname = 'public'
                      AND tablename != 'alembic_version'
                )
                LOOP
                    EXECUTE 'TRUNCATE TABLE ' || tb || ' CASCADE';
                END LOOP;
            END $$;
        """),
    )
    await session.commit()
    redis = await container.get(Redis)
    await redis.flushdb()


@pytest.fixture
async def http_session(base_url: str) -> AsyncIterator[ClientSession]:
    """Create and provide HTTP client session for API tests."""
    async with aiohttp.ClientSession(base_url=base_url) as session:
        yield session


@pytest.fixture
def base_url() -> str:
    """Get API base URL from environment variable."""
    return os.environ["API_URL"]


@pytest.fixture
async def access_token(app_config: Config) -> str:
    """Dummy access token with email_verified set to True."""
    return jwt.encode(
        {"email_verified": True},
        key=DUMMY_PRIVATE_KEY,
        algorithm=app_config.web_auth_user_id_provider.access_token_alg,
    )


@pytest.fixture
def api_client(http_session: ClientSession, app_config: Config, access_token: str) -> ApiClient:
    """Create and provide API client for tests."""
    return ApiClient(
        session=http_session,
        config=APIClientConfig(
            auth_user_id_header=app_config.web_auth_user_id_provider.user_id_header,
            auth_user_email_header=app_config.web_auth_user_id_provider.user_email_header,
            access_token_header=app_config.web_auth_user_id_provider.access_token_header,
        ),
        access_token=access_token,
    )


@pytest.fixture
def assets() -> Traversable:
    """File assets for tests."""
    return files(tests.assets)


# Polyfactory

register_fixture(ApplicationFormInputFactory)
register_fixture(SubmitApplicationInputFactory)
register_fixture(CompetitionFormFactory)
register_fixture(UpdateCompetitionFormFactory)
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
    update_competition_form_factory: UpdateCompetitionFormFactory,
) -> CompetitionGateway:
    """Gateway for competition creation and state manipulation."""
    return CompetitionGateway(
        api_client=api_client,
        session=session,
        competition_form_factory=competition_form_factory,
        update_competition_form_factory=update_competition_form_factory,
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
def gateway(
    admin_gateway: AdminGateway,
    organizer_gateway: OrganizerGateway,
    participant_gateway: ParticipantGateway,
    competition_gateway: CompetitionGateway,
    application_gateway: ApplicationGateway,
    application_form_gateway: ApplicationFormGateway,
) -> Gateway:
    """Facade providing access to all per-entity gateways."""
    return Gateway(
        admin=admin_gateway,
        organizer=organizer_gateway,
        participant=participant_gateway,
        competition=competition_gateway,
        application=application_gateway,
        application_form=application_form_gateway,
    )
