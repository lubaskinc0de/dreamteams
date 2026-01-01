import pytest
from faker import Faker

from dreamteams.entities.organizer import Organizer
from dreamteams.entities.user import User


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
