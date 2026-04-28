from datetime import timedelta
from uuid import uuid4

from dishka import AsyncContainer

from dreamteams.application.common.gateway.competition import CompetitionGateway
from dreamteams.entities.common.clock import Clock
from tests.common.factory.competition import RescheduleCompetitionFormFactory
from tests.common.helpers.competition import schedule_from_deltas
from tests.integration.api_client import ApiClient
from tests.integration.competition_helpers import competition_reschedule_form_to_model
from tests.integration.helpers.facade import Gateway


async def test_reschedule_as_owner_succeeds(
    gateway: Gateway,
    reschedule_competition_form_factory: RescheduleCompetitionFormFactory,
    request_container: AsyncContainer,
    clock: Clock,
) -> None:
    """Reschedule succeeds for the owning organizer."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    comp = await gateway.competition.create(owner.organizer.auth_id)

    update_form = reschedule_competition_form_factory.build()

    competition_gateway = await request_container.get(CompetitionGateway)
    db_competition = await competition_gateway.get(comp.created.competition_id)
    current_model = await gateway.competition.read(comp.created.competition_id, owner.organizer.auth_id)
    expected_model = competition_reschedule_form_to_model(
        current=current_model,
        form=update_form,
        updated_at=db_competition.updated_at,
        clock=clock,
    )

    # Act
    actual_model = await gateway.competition.reschedule(
        comp.created.competition_id,
        update_form,
        owner.organizer.auth_id,
    )

    # Assert
    assert actual_model.updated_at > expected_model.updated_at
    expected_model.updated_at = actual_model.updated_at
    assert actual_model == expected_model


async def test_reschedule_rejects_schedule_without_team_formation_when_team_size_is_set(
    api_client: ApiClient,
    gateway: Gateway,
    reschedule_competition_form_factory: RescheduleCompetitionFormFactory,
) -> None:
    """Reschedule rejects team size without paired team-formation dates."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    comp = await gateway.competition.create(owner.organizer.auth_id)
    data = reschedule_competition_form_factory.build().model_dump(mode="json")
    data["schedule"] = schedule_from_deltas(
        registration_start=timedelta(days=1),
        registration_end=timedelta(days=10),
    )

    # Act
    with api_client.authenticate(auth_user_id=owner.organizer.auth_id):
        response = await api_client.reschedule_competition(comp.created.competition_id, data)

    # Assert
    response.assert_error(422, "INVALID_COMPETITION_DATA")


async def test_reschedule_rejects_team_formation_without_team_size(
    api_client: ApiClient,
    gateway: Gateway,
    reschedule_competition_form_factory: RescheduleCompetitionFormFactory,
) -> None:
    """Reschedule rejects team-formation dates without paired team size."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    comp = await gateway.competition.create(owner.organizer.auth_id)
    data = reschedule_competition_form_factory.build(team_size=None).model_dump(mode="json")

    # Act
    with api_client.authenticate(auth_user_id=owner.organizer.auth_id):
        response = await api_client.reschedule_competition(comp.created.competition_id, data)

    # Assert
    response.assert_error(422, "INVALID_COMPETITION_DATA")


async def test_reschedule_fails_if_unauthorized(
    api_client: ApiClient,
    gateway: Gateway,
    reschedule_competition_form_factory: RescheduleCompetitionFormFactory,
) -> None:
    """Reschedule fails when user is unauthorized."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    comp = await gateway.competition.create(owner.organizer.auth_id)
    data = reschedule_competition_form_factory.build().model_dump(mode="json")

    # Act
    response = await api_client.reschedule_competition(comp.created.competition_id, data)

    # Assert
    response.assert_error(401, "UNAUTHORIZED")


async def test_reschedule_fails_if_not_owner(
    api_client: ApiClient,
    gateway: Gateway,
    reschedule_competition_form_factory: RescheduleCompetitionFormFactory,
) -> None:
    """Reschedule fails when user is not the owner."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    interloper = await gateway.organizer.create(owner.admin.auth_id)
    comp = await gateway.competition.create(owner.organizer.auth_id)
    data = reschedule_competition_form_factory.build().model_dump(mode="json")

    # Act
    with api_client.authenticate(auth_user_id=interloper.auth_id):
        response = await api_client.reschedule_competition(comp.created.competition_id, data)

    # Assert
    response.assert_error(403, "ACCESS_DENIED")


async def test_reschedule_fails_if_not_found(
    api_client: ApiClient,
    gateway: Gateway,
    reschedule_competition_form_factory: RescheduleCompetitionFormFactory,
) -> None:
    """Reschedule fails when competition does not exist."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    data = reschedule_competition_form_factory.build().model_dump(mode="json")

    # Act
    with api_client.authenticate(auth_user_id=owner.organizer.auth_id):
        response = await api_client.reschedule_competition(uuid4(), data)

    # Assert
    response.assert_error(404, "COMPETITION_NOT_FOUND")
