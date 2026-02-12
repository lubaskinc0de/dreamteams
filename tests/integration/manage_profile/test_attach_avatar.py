from importlib.resources import as_file
from importlib.resources.abc import Traversable

from dreamteams.application.register.register_organizer import CreatedOrganizer
from tests.integration.api_client import ApiClient


async def test_attach_avatar_to_organizer(
    api_client: ApiClient,
    assets: Traversable,
    organizer: CreatedOrganizer,  # noqa: ARG001
) -> None:
    """Test attach avatar to organizer user and then read it."""
    with as_file(assets.joinpath("valid/ya.jpg")) as path:
        attach_resp = await api_client.attach_avatar(
            path,
        )
        read_resp = await api_client.view_profile()

    attach_resp.assert_status(200)
    profile = read_resp.ensure_content()
    assert profile.avatar_url is not None
