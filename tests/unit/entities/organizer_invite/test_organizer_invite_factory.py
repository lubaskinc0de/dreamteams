import pytest
from faker import Faker

from dreamteams.entities.errors.base import AccessDeniedError
from dreamteams.entities.organizer_invite import organizer_invite_factory
from dreamteams.entities.user import User


def test_factory_non_admin_cannot_issue_invite(
    non_admin_user: User,
    faker: Faker,
) -> None:
    """Non-admin cannot create an invite."""
    with pytest.raises(AccessDeniedError):
        organizer_invite_factory(
            invite_id=faker.uuid4(cast_to=None),
            display_name=None,
            user=non_admin_user,
        )


def test_factory_creates_invite_with_correct_fields(
    admin_user: User,
    faker: Faker,
) -> None:
    """Factory sets id, display_name, created_by correctly and generates a code."""
    invite_id = faker.uuid4(cast_to=None)
    display_name = faker.word()

    invite = organizer_invite_factory(
        invite_id=invite_id,
        display_name=display_name,
        user=admin_user,
    )

    assert invite.id == invite_id
    assert invite.display_name == display_name
    assert invite.created_by == admin_user.id
    assert invite.is_revoked is False
    assert invite.is_used is False
    assert invite.used_by is None
    assert len(invite.code) > 0


def test_factory_generates_unique_codes(admin_user: User, faker: Faker) -> None:
    """Each invite gets a unique code."""
    invite_a = organizer_invite_factory(
        invite_id=faker.uuid4(cast_to=None),
        display_name=None,
        user=admin_user,
    )
    invite_b = organizer_invite_factory(
        invite_id=faker.uuid4(cast_to=None),
        display_name=None,
        user=admin_user,
    )

    assert invite_a.code != invite_b.code
