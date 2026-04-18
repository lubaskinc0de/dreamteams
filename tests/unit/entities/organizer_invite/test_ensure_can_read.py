import pytest

from dreamteams.entities.errors.base import AccessDeniedError
from tests.unit.helpers.facade import Gateway


def test_ensure_can_read_by_creator_succeeds(gateway: Gateway) -> None:
    """Admin creator can read the invite without exception."""
    admin = gateway.user.create_admin()
    invite = gateway.organizer_invite.create(creator=admin)

    invite.ensure_can_read(admin)


def test_ensure_can_read_non_admin_raises(gateway: Gateway) -> None:
    """Non-admin cannot read an invite."""
    admin = gateway.user.create_admin()
    non_admin = gateway.user.create(is_admin=False)
    invite = gateway.organizer_invite.create(creator=admin)

    with pytest.raises(AccessDeniedError):
        invite.ensure_can_read(non_admin)


def test_ensure_can_read_different_admin_raises(gateway: Gateway) -> None:
    """Admin who did not create the invite cannot read it."""
    admin = gateway.user.create_admin()
    other_admin = gateway.user.create_admin()
    invite = gateway.organizer_invite.create(creator=admin)

    with pytest.raises(AccessDeniedError):
        invite.ensure_can_read(other_admin)
