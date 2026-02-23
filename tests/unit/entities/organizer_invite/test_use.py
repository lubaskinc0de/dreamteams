import pytest

from dreamteams.entities.errors.base import AccessDeniedError
from dreamteams.entities.errors.invite import InviteAlreadyUsedError, InviteRevokedError
from dreamteams.entities.organizer_invite import OrganizerInvite
from dreamteams.entities.user import User


def test_use_succeeds_and_sets_used_by(
    invite: OrganizerInvite,
    organizer_user: User,
) -> None:
    """Using a valid invite marks it as used and records the organizer."""
    invite.use(organizer_user)

    assert invite.is_used is True
    assert invite.used_by is organizer_user.organizer


def test_use_revoked_invite_raises(
    invite: OrganizerInvite,
    admin_user: User,
    organizer_user: User,
) -> None:
    """Cannot use a revoked invite."""
    invite.revoke(admin_user)

    with pytest.raises(InviteRevokedError):
        invite.use(organizer_user)


def test_use_already_used_invite_raises(
    invite: OrganizerInvite,
    organizer_user: User,
) -> None:
    """Cannot use an invite that has already been used."""
    invite.use(organizer_user)

    with pytest.raises(InviteAlreadyUsedError):
        invite.use(organizer_user)


def test_use_without_organizer_role_raises(
    invite: OrganizerInvite,
    user_without_organizer: User,
) -> None:
    """User without organizer role cannot use an invite."""
    with pytest.raises(AccessDeniedError):
        invite.use(user_without_organizer)
