from uuid import uuid4

from dreamteams.application.manage_invites import InviteIssued, InviteModel, OrganizerInfo
from dreamteams.application.register.register_organizer import CreatedOrganizer
from dreamteams.entities.common.identifiers import UserId
from dreamteams.presentation.fast_api.routers.organizers import OrganizerForm
from tests.integration.api_client import ApiClient
from tests.integration.constants import ADMIN_USER_ID, USER_ID


async def test_admin_can_read_own_invite(
    api_client: ApiClient,
    issued_invite: InviteIssued,
    admin_user_id: UserId,
) -> None:
    """Admin can read their own invite with all correct fields."""
    with api_client.authenticate(auth_user_id=ADMIN_USER_ID):
        response = await api_client.read_invite(issued_invite.invite_id)

    result = response.assert_status(200).ensure_content()
    assert result == InviteModel(
        id=issued_invite.invite_id,
        code=issued_invite.code,
        display_name=None,
        created_by=admin_user_id,
        is_revoked=False,
        is_used=False,
        used_by=None,
        created_at=result.created_at,
    )


async def test_used_invite_shows_organizer_info(
    api_client: ApiClient,
    issued_invite: InviteIssued,
    organizer: CreatedOrganizer,
    admin_user_id: UserId,
    organizer_form: OrganizerForm,
) -> None:
    """After registration, invite used_by is populated with organizer info."""
    with api_client.authenticate(auth_user_id=ADMIN_USER_ID):
        response = await api_client.read_invite(issued_invite.invite_id)

    result = response.assert_status(200).ensure_content()
    assert result == InviteModel(
        id=issued_invite.invite_id,
        code=issued_invite.code,
        display_name=None,
        created_by=admin_user_id,
        is_revoked=False,
        is_used=True,
        used_by=OrganizerInfo(
            id=organizer.organizer_id,
            name=organizer_form.organizer_name,
            avatar_url=None,
        ),
        created_at=result.created_at,
    )


async def test_read_nonexistent_invite_fails(
    api_client: ApiClient,
    admin_user_id: UserId,  # noqa: ARG001
) -> None:
    """Reading a non-existent invite fails with INVITE_NOT_FOUND."""
    with api_client.authenticate(auth_user_id=ADMIN_USER_ID):
        response = await api_client.read_invite(uuid4())

    response.assert_error(404, "INVITE_NOT_FOUND")


async def test_non_admin_cannot_read_invite(
    api_client: ApiClient,
    issued_invite: InviteIssued,
    organizer: CreatedOrganizer,  # noqa: ARG001
    admin_user_id: UserId,  # noqa: ARG001
) -> None:
    """Non-admin users get ACCESS_DENIED when trying to read invites."""
    with api_client.authenticate(auth_user_id=USER_ID):
        response = await api_client.read_invite(issued_invite.invite_id)

    response.assert_error(403, "ACCESS_DENIED")


async def test_unauthenticated_cannot_read_invite(
    api_client: ApiClient,
    issued_invite: InviteIssued,
    admin_user_id: UserId,  # noqa: ARG001
) -> None:
    """Unauthenticated requests get UNAUTHORIZED when trying to read invites."""
    response = await api_client.read_invite(issued_invite.invite_id)

    response.assert_error(401, "UNAUTHORIZED")
