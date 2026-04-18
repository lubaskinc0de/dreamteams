import pytest

from dreamteams.entities.errors.base import AccessDeniedError
from dreamteams.entities.errors.invite import InviteAlreadyRevokedError, InviteAlreadyUsedError
from tests.unit.helpers.facade import Gateway


def test_revoke_by_admin_creator_succeeds(gateway: Gateway) -> None:
    """Admin who created the invite can revoke it."""
    admin = gateway.user.create_admin()
    invite = gateway.organizer_invite.create(creator=admin)

    invite.revoke(admin)

    assert invite.is_revoked is True


def test_revoke_non_admin_raises(gateway: Gateway) -> None:
    """Non-admin user cannot revoke an invite."""
    admin = gateway.user.create_admin()
    non_admin = gateway.user.create(is_admin=False)
    invite = gateway.organizer_invite.create(creator=admin)

    with pytest.raises(AccessDeniedError):
        invite.revoke(non_admin)


def test_revoke_different_admin_raises(gateway: Gateway) -> None:
    """Admin who did not create the invite cannot revoke it."""
    admin = gateway.user.create_admin()
    other_admin = gateway.user.create_admin()
    invite = gateway.organizer_invite.create(creator=admin)

    with pytest.raises(AccessDeniedError):
        invite.revoke(other_admin)


def test_revoke_already_used_invite_raises(gateway: Gateway) -> None:
    """Cannot revoke an invite that has already been used."""
    admin = gateway.user.create_admin()
    organizer = gateway.organizer.create()
    invite = gateway.organizer_invite.create(creator=admin)

    invite.use(organizer)

    with pytest.raises(InviteAlreadyUsedError):
        invite.revoke(admin)


def test_revoke_already_revoked_invite_raises(gateway: Gateway) -> None:
    """Cannot revoke an invite that has already been revoked."""
    admin = gateway.user.create_admin()
    invite = gateway.organizer_invite.create(creator=admin)

    invite.revoke(admin)

    with pytest.raises(InviteAlreadyRevokedError):
        invite.revoke(admin)
