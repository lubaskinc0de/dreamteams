import pytest

from dreamteams.entities.errors.invite import InviteAlreadyUsedError, InviteRevokedError
from dreamteams.entities.organizer_invite import OrganizerInvite
from dreamteams.entities.user import Organizer, User


def test_use_succeeds_and_sets_used_by(
    invite: OrganizerInvite,
    organizer: Organizer,
) -> None:
    """Using a valid invite marks it as used and records the organizer."""
    invite.use(organizer)

    assert invite.is_used is True
    assert invite.used_by is organizer


def test_use_revoked_invite_raises(
    invite: OrganizerInvite,
    admin_user: User,
    organizer: Organizer,
) -> None:
    """Cannot use a revoked invite."""
    invite.revoke(admin_user)

    with pytest.raises(InviteRevokedError):
        invite.use(organizer)


def test_use_already_used_invite_raises(
    invite: OrganizerInvite,
    organizer: Organizer,
) -> None:
    """Cannot use an invite that has already been used."""
    invite.use(organizer)

    with pytest.raises(InviteAlreadyUsedError):
        invite.use(organizer)
