from uuid import uuid4

from dreamteams.application.manage_invites import InviteIssued, InviteModel
from dreamteams.application.register.register_organizer import CreatedOrganizer
from dreamteams.entities.common.identifiers import UserId
from tests.integration.api_client import ApiClient
from tests.integration.constants import ADMIN_USER_ID, USER_ID


async def test_admin_can_revoke_own_invite(
    api_client: ApiClient,
    issued_invite: InviteIssued,
    admin_user_id: UserId,
) -> None:
    """Admin can revoke their own invite."""
    with api_client.authenticate(auth_user_id=ADMIN_USER_ID):
        response = await api_client.revoke_invite(issued_invite.invite_id)

    response.assert_status(200)
    with api_client.authenticate(auth_user_id=ADMIN_USER_ID):
        read_response = await api_client.read_invite(issued_invite.invite_id)
    result = read_response.assert_status(200).ensure_content()
    assert result == InviteModel(
        id=issued_invite.invite_id,
        code=issued_invite.code,
        display_name=None,
        created_by=admin_user_id,
        is_revoked=True,
        is_used=False,
        used_by=None,
        created_at=result.created_at,
    )


async def test_cannot_revoke_already_revoked_invite(
    api_client: ApiClient,
    issued_invite: InviteIssued,
    admin_user_id: UserId,  # noqa: ARG001
) -> None:
    """Revoking an already-revoked invite fails with INVITE_ALREADY_REVOKED."""
    with api_client.authenticate(auth_user_id=ADMIN_USER_ID):
        await api_client.revoke_invite(issued_invite.invite_id)
        response = await api_client.revoke_invite(issued_invite.invite_id)

    response.assert_error(409, "INVITE_ALREADY_REVOKED")


async def test_cannot_revoke_used_invite(
    api_client: ApiClient,
    issued_invite: InviteIssued,
    organizer: CreatedOrganizer,  # noqa: ARG001
    admin_user_id: UserId,  # noqa: ARG001
) -> None:
    """Revoking an already-used invite fails with INVITE_ALREADY_USED."""
    with api_client.authenticate(auth_user_id=ADMIN_USER_ID):
        response = await api_client.revoke_invite(issued_invite.invite_id)

    response.assert_error(409, "INVITE_ALREADY_USED")


async def test_revoke_nonexistent_invite_fails(
    api_client: ApiClient,
    admin_user_id: UserId,  # noqa: ARG001
) -> None:
    """Revoking a non-existent invite fails with INVITE_NOT_FOUND."""
    with api_client.authenticate(auth_user_id=ADMIN_USER_ID):
        response = await api_client.revoke_invite(uuid4())

    response.assert_error(404, "INVITE_NOT_FOUND")


async def test_non_admin_cannot_revoke_invite(
    api_client: ApiClient,
    issued_invite: InviteIssued,
    organizer: CreatedOrganizer,  # noqa: ARG001
) -> None:
    """Non-admin users get ACCESS_DENIED when trying to revoke invites."""
    with api_client.authenticate(auth_user_id=USER_ID):
        response = await api_client.revoke_invite(issued_invite.invite_id)

    response.assert_error(403, "ACCESS_DENIED")


async def test_unauthenticated_cannot_revoke_invite(
    api_client: ApiClient,
    issued_invite: InviteIssued,
    admin_user_id: UserId,  # noqa: ARG001
) -> None:
    """Unauthenticated requests get UNAUTHORIZED when trying to revoke invites."""
    response = await api_client.revoke_invite(issued_invite.invite_id)

    response.assert_error(401, "UNAUTHORIZED")
