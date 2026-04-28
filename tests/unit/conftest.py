from datetime import UTC, datetime
from unittest.mock import Mock

import pytest
from faker import Faker
from hypothesis import HealthCheck, settings
from polyfactory.pytest_plugin import register_fixture

from dreamteams_common.clock import Clock
from tests.common.factory.entities.organizer import OrganizerFactory
from tests.common.factory.entities.organizer_invite import OrganizerInviteFactory
from tests.common.factory.entities.participant import ParticipantDataFactory
from tests.common.factory.entities.user import UserFactory
from tests.unit.helpers.facade import Gateway
from tests.unit.helpers.organizer_gateway import OrganizerGateway
from tests.unit.helpers.organizer_invite_gateway import OrganizerInviteGateway
from tests.unit.helpers.participant_gateway import ParticipantGateway
from tests.unit.helpers.user_gateway import UserGateway

NOW_NAIVE = datetime(year=2026, month=1, day=25, hour=10, minute=30, second=25, microsecond=3)  # noqa: DTZ001
NOW = NOW_NAIVE.replace(tzinfo=UTC)


# Hypothesis

settings.register_profile(
    "unit",
    suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow],
)
settings.load_profile("unit")


@pytest.fixture(scope="session")
def clock() -> Clock:
    """Mock clock for unit tests."""
    mock_clock = Mock()
    mock_clock.now.return_value = NOW
    return mock_clock


@pytest.fixture(scope="module")
def faker() -> Faker:
    """Provide faker instance."""
    return Faker()


# Polyfactory

register_fixture(UserFactory)
register_fixture(OrganizerFactory)
register_fixture(ParticipantDataFactory)
register_fixture(OrganizerInviteFactory)


# Gateway


@pytest.fixture
def user_gateway(user_factory: type[UserFactory]) -> UserGateway:
    """Gateway for User entity construction."""
    return UserGateway(user_factory=user_factory)


@pytest.fixture
def organizer_gateway(
    organizer_factory: type[OrganizerFactory],
    user_gateway: UserGateway,
) -> OrganizerGateway:
    """Gateway for Organizer entity construction."""
    return OrganizerGateway(organizer_factory=organizer_factory, user_gateway=user_gateway)


@pytest.fixture
def participant_gateway(
    participant_data_factory: type[ParticipantDataFactory],
    user_gateway: UserGateway,
    clock: Clock,
) -> ParticipantGateway:
    """Gateway for Participant entity construction."""
    return ParticipantGateway(
        participant_data_factory=participant_data_factory,
        user_gateway=user_gateway,
        clock=clock,
    )


@pytest.fixture
def organizer_invite_gateway(user_gateway: UserGateway) -> OrganizerInviteGateway:
    """Gateway for OrganizerInvite entity construction."""
    return OrganizerInviteGateway(user_gateway=user_gateway)


@pytest.fixture
def gateway(
    user_gateway: UserGateway,
    organizer_gateway: OrganizerGateway,
    participant_gateway: ParticipantGateway,
    organizer_invite_gateway: OrganizerInviteGateway,
) -> Gateway:
    """Facade providing access to all per-entity unit-test gateways."""
    return Gateway(
        user=user_gateway,
        organizer=organizer_gateway,
        participant=participant_gateway,
        organizer_invite=organizer_invite_gateway,
    )
