import pytest

from dreamteams.entities.errors.base import AccessDeniedError
from dreamteams.entities.organizer_invite import ensure_can_list_invites
from tests.unit.helpers.facade import Gateway


def test_ensure_can_list_invites_admin_succeeds(gateway: Gateway) -> None:
    """Admin can list invites without exception."""
    admin = gateway.user.create_admin()

    ensure_can_list_invites(admin)


def test_ensure_can_list_invites_non_admin_raises(gateway: Gateway) -> None:
    """Non-admin cannot list invites."""
    non_admin = gateway.user.create(is_admin=False)

    with pytest.raises(AccessDeniedError):
        ensure_can_list_invites(non_admin)
