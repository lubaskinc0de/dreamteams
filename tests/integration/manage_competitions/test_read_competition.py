from uuid import uuid4

from dishka import AsyncContainer

from dreamteams.application.common.gateway.competition import CompetitionGateway
from dreamteams.entities.common.clock import Clock
from tests.integration.api_client import ApiClient
from tests.integration.competition_helpers import competition_form_to_model
from tests.integration.helpers.facade import Gateway


async def test_read_competition_succeeds(
    api_client: ApiClient,
    gateway: Gateway,
    request_container: AsyncContainer,
    clock: Clock,
) -> None:
    """Test reading competition by ID returns correct data."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    comp = await gateway.competition.create(owner.organizer.auth_id)

    competition_gateway = await request_container.get(CompetitionGateway)
    db_competition = await competition_gateway.get(comp.created.competition_id)

    expected_model = competition_form_to_model(
        comp.created.competition_id,
        owner.organizer.created.organizer_id,
        db_competition.created_at,
        db_competition.updated_at,
        comp.form,
        clock=clock,
    )

    # Act
    with api_client.authenticate(auth_user_id=owner.organizer.auth_id):
        actual_model = (
            (await api_client.read_competition(comp.created.competition_id)).assert_status(200).ensure_content()
        )

    # Assert
    assert actual_model == expected_model


async def test_read_competition_with_non_existent_id_fails(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """Test reading competition with non-existent ID returns 404."""
    owner = await gateway.organizer.create_with_admin(gateway.admin)

    with api_client.authenticate(auth_user_id=owner.organizer.auth_id):
        response = await api_client.read_competition(uuid4())

    response.assert_error(404, "COMPETITION_NOT_FOUND")


async def test_read_competition_by_different_organizer_fails(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """Test reading competition by different organizer returns 403."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    interloper = await gateway.organizer.create(owner.admin.auth_id)
    comp = await gateway.competition.create(owner.organizer.auth_id)

    # Act
    with api_client.authenticate(auth_user_id=interloper.auth_id):
        response = await api_client.read_competition(comp.created.competition_id)

    response.assert_error(403, "ACCESS_DENIED")


async def test_read_competition_fails_if_unauthorized(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """Test reading competition without authentication returns 401."""
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    comp = await gateway.competition.create(owner.organizer.auth_id)

    response = await api_client.read_competition(comp.created.competition_id)

    response.assert_error(401, "UNAUTHORIZED")
