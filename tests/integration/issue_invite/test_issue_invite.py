import pytest

from dreamteams.application.issue_invite import IssueInviteForm
from dreamteams.application.issue_invite.issue_invite import MAX_INVITE_DISPLAY_NAME_LENGTH
from tests.integration.api_client import ApiClient
from tests.integration.helpers.facade import Gateway


@pytest.mark.parametrize(
    "data",
    [
        {"display_name": "My invite"},
        {},
    ],
)
async def test_admin_can_issue_invite(
    api_client: ApiClient,
    gateway: Gateway,
    data: dict[str, object],
) -> None:
    """Admin can issue an invite with or without a display name."""
    # Arrange
    admin = await gateway.admin.create()

    # Act
    with api_client.authenticate(auth_user_id=admin.auth_id):
        response = await api_client.issue_invite(data)

    content = response.assert_status(200).ensure_content()

    assert content.invite_id is not None
    assert len(content.code) > 0


async def test_non_admin_cannot_issue_invite(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """Non-admin users get ACCESS_DENIED when trying to issue invites."""
    organizer = await gateway.organizer.create_with_admin(gateway.admin)

    with api_client.authenticate(auth_user_id=organizer.organizer.auth_id):
        response = await api_client.issue_invite({})

    response.assert_error(403, "ACCESS_DENIED")


async def test_issue_invite_rejects_too_long_display_name(api_client: ApiClient, gateway: Gateway) -> None:
    """Invite creation rejects oversized display names."""
    # Arrange
    admin = await gateway.admin.create()

    # Act
    with api_client.authenticate(auth_user_id=admin.auth_id):
        response = await api_client.issue_invite(
            IssueInviteForm.model_construct(
                display_name="a" * (MAX_INVITE_DISPLAY_NAME_LENGTH + 1),
            ).model_dump(mode="json"),
        )

    # Assert
    response.assert_error(422, "VALIDATION_ERROR")


async def test_unauthenticated_cannot_issue_invite(api_client: ApiClient) -> None:
    """Unauthenticated requests get UNAUTHORIZED when trying to issue invites."""
    response = await api_client.issue_invite({})

    response.assert_error(401, "UNAUTHORIZED")
