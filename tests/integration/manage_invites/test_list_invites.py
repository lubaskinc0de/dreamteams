import pytest

from dreamteams.application.manage_invites.list import PAGE_SIZE
from dreamteams.application.register.register_organizer import CreatedOrganizer
from dreamteams.entities.common.identifiers import UserId
from tests.integration.api_client import ApiClient
from tests.integration.constants import ADMIN_USER_ID, USER_ID
from tests.integration.manage_invites.helpers import create_invites, create_invites_list


@pytest.mark.parametrize("num_invites", [0, 1, 5])
async def test_admin_sees_own_invites(
    api_client: ApiClient,
    admin_user_id: UserId,  # noqa: ARG001
    num_invites: int,
) -> None:
    """Admin sees their own invites with all fields correct."""
    created = await create_invites(num_invites, api_client)

    with api_client.authenticate(auth_user_id=ADMIN_USER_ID):
        response = await api_client.list_invites()

    result = response.assert_status(200).ensure_content()
    assert result == create_invites_list(created, page=1)


@pytest.mark.parametrize("page", [1, 2, 3])
async def test_list_invites_with_pagination(
    api_client: ApiClient,
    admin_user_id: UserId,  # noqa: ARG001
    page: int,
) -> None:
    """Admin sees correct paginated results for various pages."""
    created = await create_invites(page * PAGE_SIZE, api_client)
    expected_model = create_invites_list(created, page=page)

    with api_client.authenticate(auth_user_id=ADMIN_USER_ID):
        response = await api_client.list_invites(page=page)

    result = response.assert_status(200).ensure_content()
    assert result == expected_model


async def test_non_admin_cannot_list_invites(
    api_client: ApiClient,
    organizer: CreatedOrganizer,  # noqa: ARG001
) -> None:
    """Non-admin users get ACCESS_DENIED when trying to list invites."""
    with api_client.authenticate(auth_user_id=USER_ID):
        response = await api_client.list_invites()

    response.assert_error(403, "ACCESS_DENIED")


async def test_unauthenticated_cannot_list_invites(
    api_client: ApiClient,
) -> None:
    """Unauthenticated requests get UNAUTHORIZED when trying to list invites."""
    response = await api_client.list_invites()

    response.assert_error(401, "UNAUTHORIZED")
