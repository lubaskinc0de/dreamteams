from uuid import uuid4

import pytest
from faker import Faker

from dreamteams.entities.errors.base import AccessDeniedError
from dreamteams.entities.organizer_invite import OrganizerInvite, organizer_invite_factory
from tests.unit.helpers.facade import Gateway


def test_factory_non_admin_cannot_issue_invite(gateway: Gateway) -> None:
    """Non-admin cannot create an invite."""
    non_admin = gateway.user.create(is_admin=False)

    with pytest.raises(AccessDeniedError):
        organizer_invite_factory(
            invite_id=uuid4(),
            display_name=None,
            user=non_admin,
        )


def test_factory_creates_invite_with_correct_fields(gateway: Gateway, faker: Faker) -> None:
    """Factory returns a fresh OrganizerInvite with the given id/display_name and a generated code."""
    admin = gateway.user.create_admin()
    invite_id = uuid4()
    display_name = faker.word()

    invite = organizer_invite_factory(
        invite_id=invite_id,
        display_name=display_name,
        user=admin,
    )

    assert invite == OrganizerInvite(
        id=invite_id,
        code=invite.code,
        display_name=display_name,
        created_by=admin.id,
        is_revoked=False,
        is_used=False,
        used_by=None,
        created_at=invite.created_at,
    )
    assert len(invite.code) > 0


def test_factory_generates_unique_codes(gateway: Gateway) -> None:
    """Each invite gets a unique code."""
    admin = gateway.user.create_admin()

    invite_a = gateway.organizer_invite.create(creator=admin)
    invite_b = gateway.organizer_invite.create(creator=admin)

    assert invite_a.code != invite_b.code
