from importlib.resources import as_file
from importlib.resources.abc import Traversable

import pytest
from aiohttp import ClientSession

from dreamteams.application.register.register_organizer import CreatedOrganizer
from tests.integration.api_client import ApiClient
from tests.integration.conftest import USER_ID


@pytest.mark.parametrize(
    "file_path",
    ["avatars/valid/ya.jpg"],
)
async def test_attach_avatar_to_organizer_succeeds(
    api_client: ApiClient,
    assets: Traversable,
    organizer: CreatedOrganizer,  # noqa: ARG001
    file_path: str,
) -> None:
    """Test attach avatar to organizer user."""
    with api_client.authenticate(auth_user_id=USER_ID), as_file(assets.joinpath(file_path)) as path:
        attach_resp = await api_client.attach_avatar(
            path,
        )
        read_resp = await api_client.view_profile()

    attach_resp.assert_status(200)
    profile = read_resp.ensure_content()
    assert profile.avatar_url is not None


@pytest.mark.parametrize(
    "file_path",
    ["avatars/valid/ya.jpg"],
)
async def test_view_organizer_avatar_succeeds(
    api_client: ApiClient,
    assets: Traversable,
    organizer: CreatedOrganizer,  # noqa: ARG001
    http_session: ClientSession,
    file_path: str,
) -> None:
    """Test view avatar attached to organizer."""
    with as_file(assets.joinpath(file_path)) as avatar_path:
        # Arrange
        with api_client.authenticate(auth_user_id=USER_ID):
            (
                await api_client.attach_avatar(
                    avatar_path,
                )
            ).assert_status(200)
            avatar_url = (await api_client.view_profile()).ensure_content().avatar_url
            assert avatar_url is not None

        # Act
        with api_client.authenticate(auth_user_id=USER_ID):
            async with http_session.get(avatar_url) as resp:
                # Assert
                assert resp.status == 200  # noqa: PLR2004


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
    organizer: CreatedOrganizer,  # noqa: ARG001
    file_path: str,
) -> None:
    """Test attach avatar to organizer user."""
    with api_client.authenticate(auth_user_id=USER_ID), as_file(assets.joinpath(file_path)) as path:
        attach_resp = await api_client.attach_avatar(
            path,
        )

    attach_resp.assert_error(422, "INVALID_AVATAR_ERROR")


@pytest.mark.parametrize(
    "file_path",
    ["avatars/valid/ya.jpg"],
)
async def test_cannot_attach_avatar_when_unauthorized(
    api_client: ApiClient,
    assets: Traversable,
    file_path: str,
) -> None:
    """Test attach avatar to organizer user."""
    with as_file(assets.joinpath(file_path)) as path:
        attach_resp = await api_client.attach_avatar(
            path,
        )

    attach_resp.assert_error(401, "UNAUTHORIZED")
