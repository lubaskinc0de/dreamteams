import pytest

from dreamteams.entities.errors.invite import InviteAlreadyUsedError, InviteRevokedError
from tests.unit.helpers.facade import Gateway


def test_use_succeeds_and_sets_used_by(gateway: Gateway) -> None:
    """Using a valid invite marks it as used and records the organizer."""
    admin = gateway.user.create_admin()
    organizer = gateway.organizer.create()
    invite = gateway.organizer_invite.create(creator=admin)

    invite.use(organizer)

    assert invite.is_used is True
    assert invite.used_by is organizer


def test_use_revoked_invite_raises(gateway: Gateway) -> None:
    """Cannot use a revoked invite."""
    admin = gateway.user.create_admin()
    organizer = gateway.organizer.create()
    invite = gateway.organizer_invite.create(creator=admin)

    invite.revoke(admin)

    with pytest.raises(InviteRevokedError):
        invite.use(organizer)


def test_use_already_used_invite_raises(gateway: Gateway) -> None:
    """Cannot use an invite that has already been used."""
    admin = gateway.user.create_admin()
    organizer = gateway.organizer.create()
    invite = gateway.organizer_invite.create(creator=admin)

    invite.use(organizer)

    with pytest.raises(InviteAlreadyUsedError):
        invite.use(organizer)
