import pytest

from dreamteams.entities.errors.base import AccessDeniedError
from dreamteams.entities.organizer_invite import OrganizerInvite
from dreamteams.entities.user import User


def test_ensure_can_read_by_creator_succeeds(
    invite: OrganizerInvite,
    admin_user: User,
) -> None:
    """Admin creator can read the invite without exception."""
    invite.ensure_can_read(admin_user)


def test_ensure_can_read_non_admin_raises(
    invite: OrganizerInvite,
    non_admin_user: User,
) -> None:
    """Non-admin cannot read an invite."""
    with pytest.raises(AccessDeniedError):
        invite.ensure_can_read(non_admin_user)


def test_ensure_can_read_different_admin_raises(
    invite: OrganizerInvite,
    different_admin_user: User,
) -> None:
    """Admin who did not create the invite cannot read it."""
    with pytest.raises(AccessDeniedError):
        invite.ensure_can_read(different_admin_user)
