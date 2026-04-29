from importlib.resources import as_file
from importlib.resources.abc import Traversable

import httpx
import pytest

from tests.integration.api_client import ApiClient
from tests.integration.helpers.facade import Gateway


@pytest.mark.parametrize("file_path", ["avatars/valid/ya.jpg"])
async def test_attach_avatar_to_organizer_succeeds(
    api_client: ApiClient,
    assets: Traversable,
    gateway: Gateway,
    file_path: str,
) -> None:
    """Test attach avatar to organizer user."""
    # Arrange
    organizer = await gateway.organizer.create_with_admin(gateway.admin)

    # Act
    with as_file(assets.joinpath(file_path)) as path, api_client.authenticate(auth_user_id=organizer.organizer.auth_id):
        attach_resp = await api_client.attach_avatar(path)

    # Assert
    attach_resp.assert_status(200)
    with api_client.authenticate(auth_user_id=organizer.organizer.auth_id):
        profile = (await api_client.view_profile()).ensure_content()
        assert profile.avatar_url is not None


@pytest.mark.parametrize("file_path", ["avatars/valid/ya.jpg"])
async def test_view_organizer_avatar_succeeds(
    api_client: ApiClient,
    assets: Traversable,
    gateway: Gateway,
    http_session: httpx.AsyncClient,
    file_path: str,
) -> None:
    """Test view avatar attached to organizer."""
    # Arrange
    organizer = await gateway.organizer.create_with_admin(gateway.admin)
    with (
        as_file(assets.joinpath(file_path)) as avatar_path,
        api_client.authenticate(auth_user_id=organizer.organizer.auth_id),
    ):
        (await api_client.attach_avatar(avatar_path)).assert_status(200)

        avatar_url = (await api_client.view_profile()).ensure_content().avatar_url
        assert avatar_url is not None

    # Act
    resp = await http_session.get(avatar_url)

    # Assert
    assert resp.status_code == 200


@pytest.mark.parametrize(
    "file_path",
    [
        "avatars/invalid/hello",
        "avatars/invalid/poem.txt",
    ],
)
async def test_cannot_attach_invalid_avatar(
    api_client: ApiClient,
    assets: Traversable,
    gateway: Gateway,
    file_path: str,
) -> None:
    """Test that attaching an invalid file format is rejected."""
    # Arrange
    organizer = await gateway.organizer.create_with_admin(gateway.admin)

    # Act
    with as_file(assets.joinpath(file_path)) as path, api_client.authenticate(auth_user_id=organizer.organizer.auth_id):
        attach_resp = await api_client.attach_avatar(path)

    # Assert
    attach_resp.assert_error(422, "INVALID_AVATAR_ERROR")


@pytest.mark.parametrize("file_path", ["avatars/valid/ya.jpg"])
async def test_cannot_attach_avatar_when_unauthorized(
    api_client: ApiClient,
    assets: Traversable,
    file_path: str,
) -> None:
    """Test attach avatar fails without authentication."""
    with as_file(assets.joinpath(file_path)) as path:
        attach_resp = await api_client.attach_avatar(path)

    attach_resp.assert_error(401, "UNAUTHORIZED")
