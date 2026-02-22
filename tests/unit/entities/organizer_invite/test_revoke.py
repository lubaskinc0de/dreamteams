import pytest

from dreamteams.entities.errors.base import AccessDeniedError
from dreamteams.entities.errors.invite import InviteAlreadyRevokedError, InviteAlreadyUsedError
from dreamteams.entities.organizer_invite import OrganizerInvite
from dreamteams.entities.user import User


def test_revoke_by_admin_creator_succeeds(
    invite: OrganizerInvite,
    admin_user: User,
) -> None:
    """Admin who created the invite can revoke it."""
    invite.revoke(admin_user)

    assert invite.is_revoked is True


def test_revoke_non_admin_raises(
    invite: OrganizerInvite,
    non_admin_user: User,
) -> None:
    """Non-admin user cannot revoke an invite."""
    with pytest.raises(AccessDeniedError):
        invite.revoke(non_admin_user)


def test_revoke_different_admin_raises(
    invite: OrganizerInvite,
    different_admin_user: User,
) -> None:
    """Admin who did not create the invite cannot revoke it."""
    with pytest.raises(AccessDeniedError):
        invite.revoke(different_admin_user)


def test_revoke_already_used_invite_raises(
    invite: OrganizerInvite,
    admin_user: User,
    organizer_user: User,
) -> None:
    """Cannot revoke an invite that has already been used."""
    invite.use(organizer_user)

    with pytest.raises(InviteAlreadyUsedError):
        invite.revoke(admin_user)


def test_revoke_already_revoked_invite_raises(
    invite: OrganizerInvite,
    admin_user: User,
) -> None:
    """Cannot revoke an invite that has already been revoked."""
    invite.revoke(admin_user)

    with pytest.raises(InviteAlreadyRevokedError):
        invite.revoke(admin_user)
