from uuid import uuid4

from tests.integration.api_client import ApiClient
from tests.integration.helpers.facade import Gateway


async def test_admin_can_unblock_user(api_client: ApiClient, gateway: Gateway) -> None:
    """Admin can unblock a blocked user account."""
    # Arrange
    admin = await gateway.admin.create()
    participant = await gateway.participant.create()
    with api_client.authenticate(auth_user_id=admin.auth_id):
        (await api_client.block_user(participant.created.user_id, {"reason": "policy"})).assert_status(200)

    # Act
    with api_client.authenticate(auth_user_id=admin.auth_id):
        response = await api_client.unblock_user(participant.created.user_id)

    # Assert
    response.assert_status(200)


async def test_unblocked_user_can_access_again(api_client: ApiClient, gateway: Gateway) -> None:
    """Previously blocked users can access authenticated endpoints after unblock."""
    # Arrange
    admin = await gateway.admin.create()
    participant = await gateway.participant.create()
    with api_client.authenticate(auth_user_id=admin.auth_id):
        (await api_client.block_user(participant.created.user_id, {"reason": "policy"})).assert_status(200)
    with api_client.authenticate(auth_user_id=participant.auth_id):
        (await api_client.view_profile()).assert_error(403, "ACCOUNT_BLOCKED")
    with api_client.authenticate(auth_user_id=admin.auth_id):
        (await api_client.unblock_user(participant.created.user_id)).assert_status(200)

    # Act
    with api_client.authenticate(auth_user_id=participant.auth_id):
        response = await api_client.view_profile()

    # Assert
    response.assert_status(200)


async def test_non_admin_cannot_unblock_user(api_client: ApiClient, gateway: Gateway) -> None:
    """Organizer users cannot unblock accounts."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    participant = await gateway.participant.create()
    with api_client.authenticate(auth_user_id=owner.admin.auth_id):
        (await api_client.block_user(participant.created.user_id, {"reason": "policy"})).assert_status(200)

    # Act
    with api_client.authenticate(auth_user_id=owner.organizer.auth_id):
        response = await api_client.unblock_user(participant.created.user_id)

    # Assert
    response.assert_error(403, "ACCESS_DENIED")


async def test_unblock_nonexistent_user_returns_not_found(api_client: ApiClient, gateway: Gateway) -> None:
    """Unblocking an unknown user returns USER_NOT_FOUND."""
    # Arrange
    admin = await gateway.admin.create()
    nonexistent_user_id = uuid4()

    # Act
    with api_client.authenticate(auth_user_id=admin.auth_id):
        response = await api_client.unblock_user(nonexistent_user_id)

    # Assert
    response.assert_error(404, "USER_NOT_FOUND")
