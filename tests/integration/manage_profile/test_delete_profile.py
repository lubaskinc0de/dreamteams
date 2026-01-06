from dreamteams.application.register.register_organizer import CreatedOrganizer
from tests.integration.api_client import ApiClient
from tests.integration.conftest import USER_ID


async def test_delete_profile(
    api_client: ApiClient,
    organizer: CreatedOrganizer,  # noqa: ARG001
) -> None:
    """Test viewing organizer profile."""
    with api_client.authenticate(auth_user_id=USER_ID):
        response = await api_client.delete_profile()

    with api_client.authenticate(auth_user_id=USER_ID):
        response.assert_status(200)
        (await api_client.view_profile()).assert_error(401, "UNAUTHORIZED")


async def test_delete_user_profile_fails_if_user_does_not_exist(
    api_client: ApiClient,
) -> None:
    """Test deleting user profile fails if user does not exist."""
    with api_client.authenticate(auth_user_id=USER_ID):
        response = await api_client.delete_profile()

    response.assert_error(401, "UNAUTHORIZED")


async def test_view_user_profile_fails_if_unauthorized(
    api_client: ApiClient,
) -> None:
    """Test deleting user profile fails if user is unauthorized."""
    response = await api_client.delete_profile()

    response.assert_error(401, "UNAUTHORIZED")
