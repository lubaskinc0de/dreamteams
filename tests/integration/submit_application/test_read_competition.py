from uuid import uuid4

from dishka import AsyncContainer

from dreamteams.application.common.gateway.competition import CompetitionGateway
from dreamteams.entities.common.clock import Clock
from tests.integration.api_client import ApiClient
from tests.integration.competition_helpers import competition_form_to_model
from tests.integration.helpers.facade import Gateway


async def test_participant_can_read_competition(
    api_client: ApiClient,
    gateway: Gateway,
    request_container: AsyncContainer,
    clock: Clock,
) -> None:
    """Participant receives the full competition model when reading by ID."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    participant = await gateway.participant.create()
    comp = await gateway.competition.create(owner.organizer.auth_id)

    competition_gateway = await request_container.get(CompetitionGateway)
    db_competition = await competition_gateway.get(comp.created.competition_id)
    expected_model = competition_form_to_model(
        form=comp.form,
        competition_id=comp.created.competition_id,
        organizer_id=owner.organizer.created.organizer_id,
        created_at=db_competition.created_at,
        updated_at=db_competition.updated_at,
        clock=clock,
    )

    # Act
    with api_client.authenticate(auth_user_id=participant.auth_id):
        actual_model = (
            (await api_client.read_explore_competition(comp.created.competition_id)).assert_status(200).ensure_content()
        )

    # Assert
    assert actual_model == expected_model


async def test_participant_gets_not_found_for_nonexistent_competition(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """Reading a competition that does not exist is rejected with COMPETITION_NOT_FOUND."""
    # Arrange
    participant = await gateway.participant.create()

    # Act
    with api_client.authenticate(auth_user_id=participant.auth_id):
        response = await api_client.read_explore_competition(uuid4())

    # Assert
    response.assert_error(404, "COMPETITION_NOT_FOUND")


async def test_non_participant_cannot_read_competition(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """An organizer (no participant profile) is denied with ACCESS_DENIED."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    comp = await gateway.competition.create(owner.organizer.auth_id)

    # Act
    with api_client.authenticate(auth_user_id=owner.organizer.auth_id):
        response = await api_client.read_explore_competition(comp.created.competition_id)

    # Assert
    response.assert_error(403, "ACCESS_DENIED")


async def test_unauthenticated_user_cannot_read_competition(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """Unauthenticated requests are rejected with UNAUTHORIZED."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    comp = await gateway.competition.create(owner.organizer.auth_id)

    # Act
    response = await api_client.read_explore_competition(comp.created.competition_id)

    # Assert
    response.assert_error(401, "UNAUTHORIZED")
