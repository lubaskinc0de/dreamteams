from uuid import uuid4

from dreamteams.application.issue_invite import InviteModel
from tests.integration.api_client import ApiClient
from tests.integration.helpers.facade import Gateway


async def test_admin_can_revoke_own_invite(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """Admin can revoke their own invite."""
    # Arrange
    admin = await gateway.admin.create()
    with api_client.authenticate(auth_user_id=admin.auth_id):
        invite = (await api_client.issue_invite({})).assert_status(200).ensure_content()

    # Act
    with api_client.authenticate(auth_user_id=admin.auth_id):
        response = await api_client.revoke_invite(invite.invite_id)

    # Assert
    response.assert_status(200)

    with api_client.authenticate(auth_user_id=admin.auth_id):
        result = (await api_client.read_invite(invite.invite_id)).assert_status(200).ensure_content()

    assert result == InviteModel(
        id=invite.invite_id,
        code=invite.code,
        display_name=None,
        created_by=admin.user_id,
        is_revoked=True,
        is_used=False,
        used_by=None,
        created_at=result.created_at,
    )


async def test_cannot_revoke_already_revoked_invite(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """Revoking an already-revoked invite fails with INVITE_ALREADY_REVOKED."""
    # Arrange
    admin = await gateway.admin.create()
    with api_client.authenticate(auth_user_id=admin.auth_id):
        invite = (await api_client.issue_invite({})).assert_status(200).ensure_content()
        await api_client.revoke_invite(invite.invite_id)

    # Act
    with api_client.authenticate(auth_user_id=admin.auth_id):
        response = await api_client.revoke_invite(invite.invite_id)

    # Assert
    response.assert_error(409, "INVITE_ALREADY_REVOKED")


async def test_cannot_revoke_used_invite(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """Revoking an already-used invite fails with INVITE_ALREADY_USED."""
    # Arrange
    admin = await gateway.admin.create()
    with api_client.authenticate(auth_user_id=admin.auth_id):
        invite = (await api_client.issue_invite({})).assert_status(200).ensure_content()

    await gateway.organizer.create_with_invite(invite.code)

    # Act
    with api_client.authenticate(auth_user_id=admin.auth_id):
        response = await api_client.revoke_invite(invite.invite_id)

    # Assert
    response.assert_error(409, "INVITE_ALREADY_USED")


async def test_revoke_nonexistent_invite_fails(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """Revoking a non-existent invite fails with INVITE_NOT_FOUND."""
    admin = await gateway.admin.create()

    with api_client.authenticate(auth_user_id=admin.auth_id):
        response = await api_client.revoke_invite(uuid4())

    response.assert_error(404, "INVITE_NOT_FOUND")


async def test_non_admin_cannot_revoke_invite(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """Non-admin users get ACCESS_DENIED when trying to revoke invites."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    with api_client.authenticate(auth_user_id=owner.admin.auth_id):
        invite = (await api_client.issue_invite({})).assert_status(200).ensure_content()

    # Act
    with api_client.authenticate(auth_user_id=owner.organizer.auth_id):
        response = await api_client.revoke_invite(invite.invite_id)

    # Assert
    response.assert_error(403, "ACCESS_DENIED")


async def test_unauthenticated_cannot_revoke_invite(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """Unauthenticated requests get UNAUTHORIZED when trying to revoke invites."""
    admin = await gateway.admin.create()
    with api_client.authenticate(auth_user_id=admin.auth_id):
        invite = (await api_client.issue_invite({})).assert_status(200).ensure_content()

    response = await api_client.revoke_invite(invite.invite_id)

    response.assert_error(401, "UNAUTHORIZED")
