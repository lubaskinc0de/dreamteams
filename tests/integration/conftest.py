import asyncio
import os
from collections.abc import AsyncIterable, AsyncIterator
from importlib.resources import files
from importlib.resources.abc import Traversable
from uuid import uuid4

import aiohttp
import jwt
import pytest
from aiohttp import ClientSession
from dishka import AsyncContainer
from faker import Faker
from polyfactory.pytest_plugin import register_fixture
from sqlalchemy import insert, text
from sqlalchemy.ext.asyncio import AsyncSession

import tests.assets
from dreamteams.adapters.clock import SystemClock
from dreamteams.adapters.db.models.auth_user import auth_user_table
from dreamteams.adapters.db.models.user import user_table
from dreamteams.adapters.tracing import TraceId
from dreamteams.application.manage_application_form import ApplicationFormInput, CreatedApplicationForm
from dreamteams.application.manage_competitions.read import CompetitionModel
from dreamteams.application.manage_invites import InviteIssued
from dreamteams.application.manage_my_applications import ApplicationModel
from dreamteams.application.publish_competition import CompetitionForm, CreatedCompetition
from dreamteams.application.register.register_organizer import CreatedOrganizer
from dreamteams.application.register.register_participant import CreatedParticipant, ParticipantForm
from dreamteams.application.submit_application import CreatedApplication, SubmitApplicationInput
from dreamteams.bootstrap.config.loader import Config
from dreamteams.bootstrap.di.container import get_async_container
from dreamteams.entities.common.clock import Clock
from dreamteams.entities.common.identifiers import UserId
from dreamteams.presentation.fast_api.routers.organizers import OrganizerForm
from tests.common.factory.application import SubmitApplicationInputFactory
from tests.common.factory.application_form import ApplicationFormInputFactory
from tests.common.factory.competition import CompetitionFormFactory, UpdateCompetitionFormFactory
from tests.common.factory.organizer import OrganizerFormFactory
from tests.common.factory.participant import ParticipantFormFactory
from tests.integration.api_client import ApiClient, APIClientConfig
from tests.integration.competition_helpers import activate_competition, create_mixed_competitions
from tests.integration.constants import (
    ADMIN_USER_ID,
    ANOTHER_PARTICIPANT_USER_ID,
    DIFFERENT_USER_ID,
    PARTICIPANT_USER_ID,
    USER_ID,
)
from tests.integration.manage_applications.helpers import (
    create_applications_for_competition,
    create_mixed_applications,
)
from tests.integration.manage_my_applications.helpers import create_competition_and_submit

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

# Infrastructure


@pytest.fixture(scope="session")
def clock() -> Clock:
    """Real clock."""
    return SystemClock()


@pytest.fixture
async def app_config() -> Config:
    """Load and provide app config."""
    return Config.load()


@pytest.fixture
async def trace_id() -> TraceId:
    """Generate trace id."""
    return uuid4().hex


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
) -> AsyncIterable[None]:
    """Automatically truncate all tables after each test."""
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
        {
            "email_verified": True,
        },
        key=DUMMY_PRIVATE_KEY,
        algorithm=app_config.web_auth_user_id_provider.access_token_alg,
    )


@pytest.fixture
def api_client(http_session: ClientSession, app_config: Config, trace_id: TraceId, access_token: str) -> ApiClient:
    """Create and provide API client for tests."""
    return ApiClient(
        session=http_session,
        config=APIClientConfig(
            auth_user_id_header=app_config.web_auth_user_id_provider.user_id_header,
            auth_user_email_header=app_config.web_auth_user_id_provider.user_email_header,
            access_token_header=app_config.web_auth_user_id_provider.access_token_header,
        ),
        trace_id=trace_id,
        tracing_config=app_config.tracing,
        access_token=access_token,
    )


# Mock data
register_fixture(ApplicationFormInputFactory)
register_fixture(SubmitApplicationInputFactory)
register_fixture(CompetitionFormFactory)
register_fixture(UpdateCompetitionFormFactory)
register_fixture(OrganizerFormFactory)
register_fixture(ParticipantFormFactory)


@pytest.fixture
def email(faker: Faker) -> str:
    """Fake email."""
    return faker.email()


@pytest.fixture
def organizer_form(
    organizer_form_factory: OrganizerFormFactory,
) -> OrganizerForm:
    """Organizer form."""
    return organizer_form_factory.build()


@pytest.fixture
def competition_form(
    competition_form_factory: CompetitionFormFactory,
) -> CompetitionForm:
    """Competition form."""
    return competition_form_factory.build()


@pytest.fixture
def participant_form(
    participant_form_factory: ParticipantFormFactory,
) -> ParticipantForm:
    """Participant form."""
    return participant_form_factory.build()


# Entities
@pytest.fixture
async def admin_user_id(session: AsyncSession) -> UserId:
    """Insert an admin user directly into the DB and return their UserId."""
    admin_id = uuid4()
    await session.execute(insert(user_table).values(id=admin_id, avatar=None, is_admin=True))
    await session.execute(insert(auth_user_table).values(auth_user_id=ADMIN_USER_ID, user_id=admin_id))
    await session.commit()
    return admin_id


@pytest.fixture
async def issued_invite(
    api_client: ApiClient,
    admin_user_id: UserId,  # noqa: ARG001
) -> InviteIssued:
    """Issue an organizer invite as the admin user."""
    with api_client.authenticate(auth_user_id=ADMIN_USER_ID):
        response = await api_client.issue_invite({})
    return response.assert_status(200).ensure_content()


@pytest.fixture
async def organizer(
    api_client: ApiClient,
    organizer_form: OrganizerForm,
    email: str,
    issued_invite: InviteIssued,
) -> CreatedOrganizer:
    """Created organizer entity."""
    data = {**organizer_form.model_dump(), "invite_code": issued_invite.code}
    with api_client.authenticate(auth_user_id=USER_ID, auth_user_email=email):
        response = await api_client.register_organizer(data)

    return response.assert_status(200).ensure_content()


@pytest.fixture
async def participant(
    api_client: ApiClient,
    participant_form: ParticipantForm,
    faker: Faker,
) -> CreatedParticipant:
    """Created participant entity."""
    with api_client.authenticate(auth_user_id=USER_ID, auth_user_email=faker.email()):
        response = await api_client.register_participant(data=participant_form.model_dump(mode="json"))
    return response.assert_status(200).ensure_content()


@pytest.fixture
async def different_organizer(
    api_client: ApiClient,
    organizer_form_factory: OrganizerFormFactory,
    faker: Faker,
    admin_user_id: UserId,  # noqa: ARG001
) -> CreatedOrganizer:
    """Created different organizer entity."""
    with api_client.authenticate(auth_user_id=ADMIN_USER_ID):
        invite_response = await api_client.issue_invite({})
    invite = invite_response.assert_status(200).ensure_content()

    organizer_data = organizer_form_factory.build()
    different_email = faker.email()

    with api_client.authenticate(auth_user_id=DIFFERENT_USER_ID, auth_user_email=different_email):
        response = await api_client.register_organizer({**organizer_data.model_dump(), "invite_code": invite.code})

    return response.assert_status(200).ensure_content()


@pytest.fixture
async def competition(
    api_client: ApiClient,
    organizer: CreatedOrganizer,  # noqa: ARG001
    competition_form: CompetitionForm,
) -> CreatedCompetition:
    """Created competition entity."""
    with api_client.authenticate(auth_user_id=USER_ID):
        response = await api_client.create_competition(competition_form.model_dump(mode="json"))

    return response.assert_status(200).ensure_content()


@pytest.fixture
async def non_autoaccept_competition(
    api_client: ApiClient,
    organizer: CreatedOrganizer,  # noqa: ARG001
    competition_form: CompetitionForm,
) -> CreatedCompetition:
    """Created competition with auto_accept=False so submitted applications start as PENDING."""
    form_data = {**competition_form.model_dump(mode="json"), "auto_accept": False}
    with api_client.authenticate(auth_user_id=USER_ID):
        response = await api_client.create_competition(form_data)

    return response.assert_status(200).ensure_content()


@pytest.fixture
async def active_competition(
    api_client: ApiClient,
    organizer: CreatedOrganizer,  # noqa: ARG001
    competition_form: CompetitionForm,
    update_competition_form_factory: UpdateCompetitionFormFactory,
    session: AsyncSession,
) -> CreatedCompetition:
    """Competition with open registration, not archived, ANY participant type, high participant limit."""
    with api_client.authenticate(auth_user_id=USER_ID):
        created = (
            (await api_client.create_competition(competition_form.model_dump(mode="json")))
            .assert_status(200)
            .ensure_content()
        )

    await activate_competition(
        api_client,
        session,
        update_competition_form_factory,
        created.competition_id,
        domains=competition_form.domains,
        auto_accept=competition_form.auto_accept,
    )

    return created


@pytest.fixture
async def active_non_autoaccept_competition(
    api_client: ApiClient,
    organizer: CreatedOrganizer,  # noqa: ARG001
    competition_form: CompetitionForm,
    update_competition_form_factory: UpdateCompetitionFormFactory,
    session: AsyncSession,
) -> CreatedCompetition:
    """Competition with open registration, not archived, auto_accept=False, ANY participant type."""
    form_data = {**competition_form.model_dump(mode="json"), "auto_accept": False}
    with api_client.authenticate(auth_user_id=USER_ID):
        created = (await api_client.create_competition(form_data)).assert_status(200).ensure_content()

    await activate_competition(
        api_client,
        session,
        update_competition_form_factory,
        created.competition_id,
        domains=competition_form.domains,
        auto_accept=False,
    )

    return created


@pytest.fixture
def application_form_input(
    application_form_input_factory: ApplicationFormInputFactory,
) -> ApplicationFormInput:
    """Valid ApplicationFormInput built by the factory."""
    return application_form_input_factory.build()


@pytest.fixture
def submit_application_input(
    submit_application_input_factory: SubmitApplicationInputFactory,
    competition_form: CompetitionForm,
) -> SubmitApplicationInput:
    """Valid SubmitApplicationInput with domains guaranteed to be a subset of the competition's domains."""
    return submit_application_input_factory.build(domains=[competition_form.domains[0]], form_data=None)


@pytest.fixture
async def created_application_form(
    api_client: ApiClient,
    competition: CreatedCompetition,
    application_form_input: ApplicationFormInput,
) -> CreatedApplicationForm:
    """Created application form attached to the competition owned by USER_ID."""
    with api_client.authenticate(auth_user_id=USER_ID):
        response = await api_client.create_application_form(
            competition.competition_id,
            application_form_input.model_dump(mode="json"),
        )
    return response.assert_status(200).ensure_content()


@pytest.fixture
async def different_participant(
    api_client: ApiClient,
    participant_form_factory: ParticipantFormFactory,
    faker: Faker,
) -> CreatedParticipant:
    """Created participant entity using PARTICIPANT_USER_ID."""
    form = participant_form_factory.build()
    with api_client.authenticate(auth_user_id=PARTICIPANT_USER_ID, auth_user_email=faker.email()):
        response = await api_client.register_participant(data=form.model_dump(mode="json"))
    return response.assert_status(200).ensure_content()


@pytest.fixture
async def another_participant(
    api_client: ApiClient,
    participant_form_factory: ParticipantFormFactory,
    faker: Faker,
) -> CreatedParticipant:
    """Created participant entity using ANOTHER_PARTICIPANT_USER_ID."""
    form = participant_form_factory.build()
    with api_client.authenticate(auth_user_id=ANOTHER_PARTICIPANT_USER_ID, auth_user_email=faker.email()):
        response = await api_client.register_participant(data=form.model_dump(mode="json"))
    return response.assert_status(200).ensure_content()


@pytest.fixture
async def submitted_application(
    api_client: ApiClient,
    different_participant: CreatedParticipant,  # noqa: ARG001
    active_non_autoaccept_competition: CreatedCompetition,
    submit_application_input: SubmitApplicationInput,
) -> CreatedApplication:
    """Application submitted by PARTICIPANT_USER_ID participant to the competition owned by USER_ID."""
    with api_client.authenticate(auth_user_id=PARTICIPANT_USER_ID):
        response = await api_client.submit_application(
            active_non_autoaccept_competition.competition_id,
            submit_application_input.model_dump(mode="json"),
        )
    return response.assert_status(200).ensure_content()


@pytest.fixture(params=[0, 1, 5, 10])
async def applications(
    api_client: ApiClient,
    organizer: CreatedOrganizer,  # noqa: ARG001
    active_non_autoaccept_competition: CreatedCompetition,
    submit_application_input: SubmitApplicationInput,
    participant_form_factory: ParticipantFormFactory,
    faker: Faker,
    request: pytest.FixtureRequest,
) -> list[ApplicationModel]:
    """Applications with mixed statuses submitted to the competition (0, 1, 5, or 10 applications)."""
    num_applications: int = request.param
    submitted_ids = await create_applications_for_competition(
        num_applications,
        api_client,
        active_non_autoaccept_competition.competition_id,
        submit_application_input,
        participant_form_factory,
        faker,
    )
    return await create_mixed_applications(api_client, submitted_ids)


@pytest.fixture(params=[0, 1, 5, 10])
async def my_applications(
    api_client: ApiClient,
    different_participant: CreatedParticipant,  # noqa: ARG001
    organizer: CreatedOrganizer,  # noqa: ARG001
    competition_form_factory: CompetitionFormFactory,
    update_competition_form_factory: UpdateCompetitionFormFactory,
    submit_application_input_factory: SubmitApplicationInputFactory,
    session: AsyncSession,
    request: pytest.FixtureRequest,
) -> list[ApplicationModel]:
    """N applications submitted by PARTICIPANT_USER_ID to separate competitions, with mixed statuses."""
    num_applications: int = request.param
    submitted_ids = []
    for _ in range(num_applications):
        app_id = await create_competition_and_submit(
            api_client,
            competition_form_factory,
            update_competition_form_factory,
            submit_application_input_factory,
            session,
        )
        submitted_ids.append(app_id)
    return await create_mixed_applications(api_client, submitted_ids)


async def create_competitions(
    num_competitions: int,
    competition_form_factory: CompetitionFormFactory,
    api_client: ApiClient,
    user_id: str = USER_ID,
) -> list[CompetitionModel]:
    """Create and read competitions."""
    forms = [competition_form_factory.build() for _ in range(num_competitions)]
    with api_client.authenticate(auth_user_id=user_id):
        created_responses = await asyncio.gather(
            *[api_client.create_competition(form.model_dump(mode="json")) for form in forms],
        )
        created = [response.assert_status(200).ensure_content() for response in created_responses]
        read_responses = await asyncio.gather(*[api_client.read_competition(c.competition_id) for c in created])
        return [response.assert_status(200).ensure_content() for response in read_responses]


async def create_competition(
    competition_form: CompetitionForm,
    api_client: ApiClient,
) -> CompetitionModel:
    """Create and read competition."""
    competition_id = (
        (await api_client.create_competition(competition_form.model_dump(mode="json")))
        .assert_status(200)
        .ensure_content()
        .competition_id
    )
    return (await api_client.read_competition(competition_id)).assert_status(200).ensure_content()


@pytest.fixture
def assets() -> Traversable:
    """File assets for tests."""
    return files(tests.assets)


@pytest.fixture(params=[0, 1, 5, 10])
async def competitions(
    api_client: ApiClient,
    competition_form_factory: CompetitionFormFactory,
    request: pytest.FixtureRequest,
    organizer: CreatedOrganizer,  # noqa: ARG001
    session: AsyncSession,
) -> list[CompetitionModel]:
    """Create and read competitions with mixed states (active, inactive, archived, passed)."""
    num_competitions = request.param
    base_competitions = await create_competitions(num_competitions, competition_form_factory, api_client)
    return await create_mixed_competitions(session, api_client, base_competitions)
