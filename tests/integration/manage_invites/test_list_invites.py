import pytest

from dreamteams.application.manage_invites.list import PAGE_SIZE
from tests.integration.api_client import ApiClient
from tests.integration.helpers.facade import Gateway
from tests.integration.manage_invites.helpers import create_invites_list


@pytest.mark.parametrize("num_invites", [0, 1, 5])
async def test_admin_sees_own_invites(
    api_client: ApiClient,
    gateway: Gateway,
    num_invites: int,
) -> None:
    """Admin sees their own invites with all fields correct."""
    # Arrange
    admin = await gateway.admin.create()
    created = await gateway.admin.create_invites(admin.auth_id, num_invites)

    # Act
    with api_client.authenticate(auth_user_id=admin.auth_id):
        response = await api_client.list_invites()

    result = response.assert_status(200).ensure_content()
    assert result == create_invites_list(created, page=1)


@pytest.mark.parametrize("page", [1, 2, 3])
async def test_list_invites_with_pagination(
    api_client: ApiClient,
    gateway: Gateway,
    page: int,
) -> None:
    """Admin sees correct paginated results for various pages."""
    # Arrange
    admin = await gateway.admin.create()
    created = await gateway.admin.create_invites(admin.auth_id, page * PAGE_SIZE)
    expected_model = create_invites_list(created, page=page)

    # Act
    with api_client.authenticate(auth_user_id=admin.auth_id):
        response = await api_client.list_invites(page=page)

    result = response.assert_status(200).ensure_content()
    assert result == expected_model


async def test_non_admin_cannot_list_invites(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """Non-admin users get ACCESS_DENIED when trying to list invites."""
    organizer = await gateway.organizer.create_with_admin(gateway.admin)

    with api_client.authenticate(auth_user_id=organizer.organizer.auth_id):
        response = await api_client.list_invites()

    response.assert_error(403, "ACCESS_DENIED")


async def test_unauthenticated_cannot_list_invites(api_client: ApiClient) -> None:
    """Unauthenticated requests get UNAUTHORIZED when trying to list invites."""
    response = await api_client.list_invites()

    response.assert_error(401, "UNAUTHORIZED")
