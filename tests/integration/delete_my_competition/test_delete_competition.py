from uuid import uuid4

from tests.integration.api_client import ApiClient
from tests.integration.helpers.facade import Gateway


async def test_delete_competition_as_owner_succeeds(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """Test deleting competition by owner organizer."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    comp = await gateway.competition.create(owner.organizer.auth_id)

    # Act
    with api_client.authenticate(auth_user_id=owner.organizer.auth_id):
        response = await api_client.delete_competition(comp.created.competition_id)
        read_response = await api_client.read_competition(comp.created.competition_id)

    # Assert
    response.assert_status(200)
    read_response.assert_status(404)


async def test_delete_competition_fails_if_not_found(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """Test deleting non-existent competition."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    non_existent_id = uuid4()

    # Act
    with api_client.authenticate(auth_user_id=owner.organizer.auth_id):
        response = await api_client.delete_competition(non_existent_id)

    # Assert
    response.assert_error(404, "COMPETITION_NOT_FOUND")


async def test_delete_competition_fails_if_not_owner(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """Test deleting competition by different organizer."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    interloper = await gateway.organizer.create(owner.admin.auth_id)
    comp = await gateway.competition.create(owner.organizer.auth_id)

    # Act
    with api_client.authenticate(auth_user_id=interloper.auth_id):
        response = await api_client.delete_competition(comp.created.competition_id)

    # Assert
    response.assert_error(403, "ACCESS_DENIED")


async def test_delete_competition_fails_if_user_has_no_organizer_role(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """Test deleting competition fails when user has no organizer role."""
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    participant = await gateway.participant.create()
    comp = await gateway.competition.create(owner.organizer.auth_id)

    with api_client.authenticate(auth_user_id=participant.auth_id):
        response = await api_client.delete_competition(comp.created.competition_id)

    response.assert_error(404, "ORGANIZER_NOT_FOUND")


async def test_delete_competition_fails_if_unauthorized(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """Test deleting competition fails when user is unauthorized."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    comp = await gateway.competition.create(owner.organizer.auth_id)

    # Act
    response = await api_client.delete_competition(comp.created.competition_id)

    # Assert
    response.assert_error(401, "UNAUTHORIZED")
