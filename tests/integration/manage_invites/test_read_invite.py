from uuid import uuid4

from dreamteams.application.manage_invites import InviteModel, OrganizerInfo
from tests.integration.api_client import ApiClient
from tests.integration.helpers.facade import Gateway


async def test_admin_can_read_own_invite(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """Admin can read their own invite with all correct fields."""
    # Arrange
    admin = await gateway.admin.create()
    with api_client.authenticate(auth_user_id=admin.auth_id):
        invite = (await api_client.issue_invite({})).assert_status(200).ensure_content()

    # Act
    with api_client.authenticate(auth_user_id=admin.auth_id):
        response = await api_client.read_invite(invite.invite_id)

    result = response.assert_status(200).ensure_content()
    assert result == InviteModel(
        id=invite.invite_id,
        code=invite.code,
        display_name=None,
        created_by=admin.user_id,
        is_revoked=False,
        is_used=False,
        used_by=None,
        created_at=result.created_at,
    )


async def test_used_invite_shows_organizer_info(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """After registration, invite used_by is populated with organizer info."""
    # Arrange
    admin = await gateway.admin.create()
    with api_client.authenticate(auth_user_id=admin.auth_id):
        invite = (await api_client.issue_invite({})).assert_status(200).ensure_content()

    organizer = await gateway.organizer.create_with_invite(invite.code)

    # Act
    with api_client.authenticate(auth_user_id=admin.auth_id):
        response = await api_client.read_invite(invite.invite_id)

    result = response.assert_status(200).ensure_content()
    assert result == InviteModel(
        id=invite.invite_id,
        code=invite.code,
        display_name=None,
        created_by=admin.user_id,
        is_revoked=False,
        is_used=True,
        used_by=OrganizerInfo(
            id=organizer.created.organizer_id,
            name=organizer.form.organizer_name,
            avatar_url=None,
        ),
        created_at=result.created_at,
    )


async def test_read_nonexistent_invite_fails(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """Reading a non-existent invite fails with INVITE_NOT_FOUND."""
    admin = await gateway.admin.create()

    with api_client.authenticate(auth_user_id=admin.auth_id):
        response = await api_client.read_invite(uuid4())

    response.assert_error(404, "INVITE_NOT_FOUND")


async def test_non_admin_cannot_read_invite(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """Non-admin users get ACCESS_DENIED when trying to read invites."""
    # Arrange
    admin = await gateway.admin.create()
    with api_client.authenticate(auth_user_id=admin.auth_id):
        invite = (await api_client.issue_invite({})).assert_status(200).ensure_content()

    organizer = await gateway.organizer.create_with_invite(invite.code)

    # Act
    with api_client.authenticate(auth_user_id=organizer.auth_id):
        response = await api_client.read_invite(invite.invite_id)

    response.assert_error(403, "ACCESS_DENIED")


async def test_unauthenticated_cannot_read_invite(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """Unauthenticated requests get UNAUTHORIZED when trying to read invites."""
    admin = await gateway.admin.create()
    with api_client.authenticate(auth_user_id=admin.auth_id):
        invite = (await api_client.issue_invite({})).assert_status(200).ensure_content()

    response = await api_client.read_invite(invite.invite_id)

    response.assert_error(401, "UNAUTHORIZED")
