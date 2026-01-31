from datetime import UTC, datetime
from unittest.mock import Mock

import pytest
from faker import Faker

from dreamteams.entities.common.clock import Clock
from dreamteams.entities.organizer import Organizer
from dreamteams.entities.user import User

NOW_NAIVE = datetime(year=2026, month=1, day=25, hour=10, minute=30, second=25, microsecond=3)  # noqa: DTZ001
NOW = NOW_NAIVE.replace(tzinfo=UTC)


@pytest.fixture(scope="session")
def clock() -> Clock:
    """Mock clock for unit tests."""
    mock_clock = Mock()
    mock_clock.now.return_value = NOW
    return mock_clock


@pytest.fixture
def organizer_user(faker: Faker) -> User:
    """User with organizer role attached."""
    user_id = faker.uuid4(cast_to=None)
    organizer_id = faker.uuid4(cast_to=None)

    organizer = Organizer(
        id=organizer_id,
        user_id=user_id,
        organizer_name=faker.company(),
        phone_number=faker.phone_number(),
        contact_email=faker.email(),
        logo=None,
    )

    return User(id=user_id, organizer=organizer)


@pytest.fixture
def different_user(faker: Faker) -> User:
    """Different user with different organizer role attached."""
    user_id = faker.uuid4(cast_to=None)
    organizer_id = faker.uuid4(cast_to=None)

    organizer = Organizer(
        id=organizer_id,
        user_id=user_id,
        organizer_name=faker.company(),
        phone_number=faker.phone_number(),
        contact_email=faker.email(),
        logo=None,
    )

    return User(id=user_id, organizer=organizer)


@pytest.fixture
def user_without_organizer(faker: Faker) -> User:
    """User without organizer role."""
    return User(id=faker.uuid4(cast_to=None), organizer=None)


@pytest.fixture(scope="module")
def faker() -> Faker:
    """Provide faker instance."""
    return Faker()
