from uuid import uuid4

from tests.integration.api_client import ApiClient
from tests.integration.helpers.facade import Gateway


async def test_delete_profile(api_client: ApiClient, gateway: Gateway) -> None:
    """Test deleting organizer profile removes the user."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    await gateway.competition.create(owner.organizer.auth_id)

    # Act
    with api_client.authenticate(auth_user_id=owner.organizer.auth_id):
        response = await api_client.delete_profile()

    # Assert
    response.assert_status(200)

    with api_client.authenticate(auth_user_id=owner.organizer.auth_id):
        (await api_client.view_profile()).assert_error(404, "USER_NOT_FOUND")


async def test_delete_user_profile_fails_if_user_does_not_exist(api_client: ApiClient) -> None:
    """Test deleting user profile fails if user does not exist."""
    with api_client.authenticate(auth_user_id=str(uuid4())):
        response = await api_client.delete_profile()

    response.assert_error(401, "UNAUTHORIZED")


async def test_view_user_profile_fails_if_unauthorized(api_client: ApiClient) -> None:
    """Test deleting user profile fails if user is unauthorized."""
    response = await api_client.delete_profile()

    response.assert_error(401, "UNAUTHORIZED")
