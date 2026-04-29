from importlib.resources import as_file
from importlib.resources.abc import Traversable

import pytest

from tests.integration.api_client import ApiClient
from tests.integration.helpers.facade import Gateway


@pytest.mark.parametrize("file_path", ["avatars/valid/ya.jpg"])
async def test_detach_avatar_from_organizer_succeeds(
    api_client: ApiClient,
    assets: Traversable,
    gateway: Gateway,
    file_path: str,
) -> None:
    """Test detach avatar from organizer user."""
    # Arrange
    organizer = await gateway.organizer.create_with_admin(gateway.admin)

    with as_file(assets.joinpath(file_path)) as path, api_client.authenticate(auth_user_id=organizer.organizer.auth_id):
        (await api_client.attach_avatar(path)).assert_status(200)

    # Act
    with api_client.authenticate(auth_user_id=organizer.organizer.auth_id):
        detach_resp = await api_client.detach_avatar()

    # Assert
    detach_resp.assert_status(200)
    with api_client.authenticate(auth_user_id=organizer.organizer.auth_id):
        profile = (await api_client.view_profile()).ensure_content()
        assert profile.avatar_url is None


async def test_detach_avatar_when_no_avatar_succeeds(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """Test detach avatar when user has no avatar."""
    # Arrange
    organizer = await gateway.organizer.create_with_admin(gateway.admin)

    # Act
    with api_client.authenticate(auth_user_id=organizer.organizer.auth_id):
        detach_resp = await api_client.detach_avatar()

    # Assert
    detach_resp.assert_status(200)
    with api_client.authenticate(auth_user_id=organizer.organizer.auth_id):
        profile = (await api_client.view_profile()).ensure_content()
        assert profile.avatar_url is None


async def test_cannot_detach_avatar_when_unauthorized(
    api_client: ApiClient,
) -> None:
    """Test detach avatar without authentication fails."""
    # Act
    detach_resp = await api_client.detach_avatar()

    # Assert
    detach_resp.assert_error(401, "UNAUTHORIZED")
