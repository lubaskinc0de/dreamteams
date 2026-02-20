import pytest

from dreamteams.application.register.register_organizer import CreatedOrganizer
from dreamteams.entities.common.identifiers import UserId
from tests.integration.api_client import ApiClient
from tests.integration.constants import ADMIN_USER_ID, USER_ID


@pytest.mark.parametrize(
    "data",
    [
        {"display_name": "My invite"},
        {},
    ],
)
async def test_admin_can_issue_invite(
    api_client: ApiClient,
    admin_user_id: UserId,  # noqa: ARG001
    data: dict[str, object],
) -> None:
    """Admin can issue an invite with or without a display name."""
    with api_client.authenticate(auth_user_id=ADMIN_USER_ID):
        response = await api_client.issue_invite(data)

    content = response.assert_status(200).ensure_content()

    assert content.invite_id is not None
    assert len(content.code) > 0


async def test_non_admin_cannot_issue_invite(
    api_client: ApiClient,
    organizer: CreatedOrganizer,  # noqa: ARG001
) -> None:
    """Non-admin users get ACCESS_DENIED when trying to issue invites."""
    with api_client.authenticate(auth_user_id=USER_ID):
        response = await api_client.issue_invite({})

    response.assert_error(403, "ACCESS_DENIED")


async def test_unauthenticated_cannot_issue_invite(
    api_client: ApiClient,
) -> None:
    """Unauthenticated requests get UNAUTHORIZED when trying to issue invites."""
    response = await api_client.issue_invite({})

    response.assert_error(401, "UNAUTHORIZED")
