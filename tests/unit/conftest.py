from datetime import UTC, datetime
from unittest.mock import Mock

import pytest
from faker import Faker

from dreamteams.entities.common.clock import Clock
from dreamteams.entities.user import Organizer, User

NOW_NAIVE = datetime(year=2026, month=1, day=25, hour=10, minute=30, second=25, microsecond=3)  # noqa: DTZ001
NOW = NOW_NAIVE.replace(tzinfo=UTC)


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


@pytest.fixture
def organizer(faker: Faker) -> Organizer:
    """Standalone Organizer entity tied to a fresh User."""
    user_id = faker.uuid4(cast_to=None)
    user = User(id=user_id, organizer=None)
    return Organizer(
        id=faker.uuid4(cast_to=None),
        user_id=user_id,
        user=user,
        organizer_name=faker.company(),
        phone_number=faker.phone_number(),
        contact_email=faker.email(),
    )


@pytest.fixture
def different_organizer(faker: Faker) -> Organizer:
    """Different Organizer entity tied to a different fresh User."""
    user_id = faker.uuid4(cast_to=None)
    user = User(id=user_id, organizer=None)
    return Organizer(
        id=faker.uuid4(cast_to=None),
        user_id=user_id,
        user=user,
        organizer_name=faker.company(),
        phone_number=faker.phone_number(),
        contact_email=faker.email(),
    )


@pytest.fixture
def user_without_organizer(faker: Faker) -> User:
    """User without organizer role (used by participant tests for User.id source)."""
    return User(id=faker.uuid4(cast_to=None), organizer=None)
