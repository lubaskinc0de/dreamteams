from importlib.resources import as_file
from importlib.resources.abc import Traversable

import pytest

from dreamteams.application.register.register_organizer import CreatedOrganizer
from tests.integration.api_client import ApiClient
from tests.integration.conftest import USER_ID


@pytest.mark.parametrize(
    "file_path",
    ["avatars/valid/ya.jpg"],
)
async def test_detach_avatar_from_organizer_succeeds(
    api_client: ApiClient,
    assets: Traversable,
    organizer: CreatedOrganizer,  # noqa: ARG001
    file_path: str,
) -> None:
    """Test detach avatar from organizer user."""
    with api_client.authenticate(auth_user_id=USER_ID), as_file(assets.joinpath(file_path)) as path:
        (await api_client.attach_avatar(path)).assert_status(200)

        detach_resp = await api_client.detach_avatar()

        detach_resp.assert_status(200)
        profile = (await api_client.view_profile()).ensure_content()
        assert profile.avatar_url is None


async def test_detach_avatar_when_no_avatar_succeeds(
    api_client: ApiClient,
    organizer: CreatedOrganizer,  # noqa: ARG001
) -> None:
    """Test detach avatar when user has no avatar."""
    with api_client.authenticate(auth_user_id=USER_ID):
        detach_resp = await api_client.detach_avatar()

        detach_resp.assert_status(200)
        profile = (await api_client.view_profile()).ensure_content()
        assert profile.avatar_url is None


async def test_cannot_detach_avatar_when_unauthorized(
    api_client: ApiClient,
) -> None:
    """Test detach avatar without authentication fails."""
    detach_resp = await api_client.detach_avatar()

    detach_resp.assert_error(401, "UNAUTHORIZED")
