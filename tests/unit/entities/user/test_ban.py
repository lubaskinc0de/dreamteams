import pytest

from dreamteams.entities.common.clock import Clock
from dreamteams.entities.errors.base import AccessDeniedError
from dreamteams.entities.user import BanStatus
from tests.unit.conftest import NOW
from tests.unit.helpers.facade import Gateway


def test_block_sets_ban_status_with_reason(gateway: Gateway, clock: Clock) -> None:
    """Admin blocking stores the blocked status, reason, and timestamp."""
    # Arrange
    admin = gateway.user.create_admin()
    user = gateway.user.create()
    reason = "Terms violation"

    # Act
    user.block(admin=admin, reason=reason, clock=clock)

    # Assert
    assert user.ban_status == BanStatus(is_blocked=True, reason=reason, blocked_at=NOW)


def test_block_without_reason_stores_none_reason(gateway: Gateway, clock: Clock) -> None:
    """Admin can block a user without providing a reason."""
    # Arrange
    admin = gateway.user.create_admin()
    user = gateway.user.create()

    # Act
    user.block(admin=admin, reason=None, clock=clock)

    # Assert
    assert user.ban_status == BanStatus(is_blocked=True, reason=None, blocked_at=NOW)


def test_block_by_non_admin_raises(gateway: Gateway, clock: Clock) -> None:
    """Non-admin users cannot block accounts."""
    # Arrange
    non_admin = gateway.user.create(is_admin=False)
    user = gateway.user.create()

    # Act / Assert
    with pytest.raises(AccessDeniedError):
        user.block(admin=non_admin, reason="not allowed", clock=clock)


def test_unblock_clears_ban_status(gateway: Gateway, clock: Clock) -> None:
    """Admin unblocking clears the blocked status."""
    # Arrange
    admin = gateway.user.create_admin()
    user = gateway.user.create()
    user.block(admin=admin, reason="temporary", clock=clock)

    # Act
    user.unblock(admin=admin)

    # Assert
    assert user.ban_status == BanStatus(is_blocked=False)


def test_unblock_by_non_admin_raises(gateway: Gateway, clock: Clock) -> None:
    """Non-admin users cannot unblock accounts."""
    # Arrange
    admin = gateway.user.create_admin()
    non_admin = gateway.user.create(is_admin=False)
    user = gateway.user.create()
    user.block(admin=admin, reason="temporary", clock=clock)

    # Act / Assert
    with pytest.raises(AccessDeniedError):
        user.unblock(admin=non_admin)


def test_default_ban_status_is_not_blocked(gateway: Gateway) -> None:
    """Fresh users start unblocked."""
    # Act
    user = gateway.user.create()

    # Assert
    assert user.ban_status == BanStatus(is_blocked=False)
