import pytest
from faker import Faker

from dreamteams.entities.organizer_invite import OrganizerInvite, organizer_invite_factory
from dreamteams.entities.user import User


@pytest.fixture
def non_admin_user(faker: Faker) -> User:
    """Regular user without admin privileges and without organizer role."""
    return User(id=faker.uuid4(cast_to=None), organizer=None, is_admin=False)


@pytest.fixture
def admin_user(faker: Faker) -> User:
    """Admin user without organizer role."""
    return User(id=faker.uuid4(cast_to=None), organizer=None, is_admin=True)


@pytest.fixture
def different_admin_user(faker: Faker) -> User:
    """Different admin user (not the invite creator)."""
    return User(id=faker.uuid4(cast_to=None), organizer=None, is_admin=True)


@pytest.fixture
def invite(faker: Faker, admin_user: User) -> OrganizerInvite:
    """A fresh (unused, unrevoked) invite created by admin_user."""
    return organizer_invite_factory(
        invite_id=faker.uuid4(cast_to=None),
        display_name=None,
        user=admin_user,
    )
