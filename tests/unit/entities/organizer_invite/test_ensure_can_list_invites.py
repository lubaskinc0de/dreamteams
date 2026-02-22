import pytest

from dreamteams.entities.errors.base import AccessDeniedError
from dreamteams.entities.organizer_invite import ensure_can_list_invites
from dreamteams.entities.user import User


def test_ensure_can_list_invites_admin_succeeds(admin_user: User) -> None:
    """Admin can list invites without exception."""
    ensure_can_list_invites(admin_user)


def test_ensure_can_list_invites_non_admin_raises(non_admin_user: User) -> None:
    """Non-admin cannot list invites."""
    with pytest.raises(AccessDeniedError):
        ensure_can_list_invites(non_admin_user)
