from typing import Any

import pytest
from dishka import AsyncContainer
from faker import Faker

from dreamteams.application.common.gateway.competition import CompetitionGateway
from dreamteams.application.publish_competition import CreatedCompetition
from dreamteams.application.register.register_organizer import CreatedOrganizer
from dreamteams.entities.common.clock import Clock
from tests.common.factory.competition import UpdateCompetitionFormFactory
from tests.common.helpers.competition import (
    INVALID_COMPETITION_DATA_CASES,
    milestones_from_deltas,
    schedule_from_deltas,
)
from tests.integration.api_client import ApiClient
from tests.integration.constants import DIFFERENT_USER_ID, USER_ID
from tests.integration.manage_competitions.helpers import competition_update_form_to_model


async def test_update_competition_as_owner_succeeds(
    api_client: ApiClient,
    competition: CreatedCompetition,
    update_competition_form_factory: UpdateCompetitionFormFactory,
    request_container: AsyncContainer,
    clock: Clock,
) -> None:
    """Test updating competition as owner."""
    update_form = update_competition_form_factory.build()
    data = update_form.model_dump(mode="json")
    competition_gateway = await request_container.get(CompetitionGateway)
    db_competition = await competition_gateway.get(competition.competition_id)
    expected_model = competition_update_form_to_model(
        competition_id=competition.competition_id,
        updated_at=db_competition.updated_at,
        created_at=db_competition.created_at,
        organizer_id=db_competition.organizer_id,
        form=update_form,
        clock=clock,
    )

    with api_client.authenticate(auth_user_id=USER_ID):
        update_response = await api_client.update_competition(competition.competition_id, data)
        update_response.assert_status(200)

        read_response = await api_client.read_competition(competition.competition_id)

    actual_model = read_response.assert_status(200).ensure_content()
    assert actual_model.updated_at > expected_model.updated_at
    expected_model.updated_at = actual_model.updated_at
    assert actual_model == expected_model


@pytest.mark.parametrize(("update_data", "expected_error"), INVALID_COMPETITION_DATA_CASES)
async def test_update_competition_with_invalid_data(
    api_client: ApiClient,
    competition: CreatedCompetition,
    update_competition_form_factory: UpdateCompetitionFormFactory,
    update_data: dict[str, Any],
    expected_error: str,
) -> None:
    """Test updating competition with invalid data."""
    # Arrange
    base_data = update_competition_form_factory.build().model_dump(mode="json")
    update_data = update_data.copy()

    if "schedule" in update_data:
        schedule = update_data["schedule"]
        update_data["schedule"] = schedule_from_deltas(**schedule)

    if "milestones" in update_data:
        update_data["milestones"] = milestones_from_deltas(update_data["milestones"])

    base_data.update(update_data)

    # Act
    with api_client.authenticate(auth_user_id=USER_ID):
        response = await api_client.update_competition(competition.competition_id, base_data)

    # Assert
    response.assert_error(422, expected_error)


async def test_update_competition_fails_if_unauthorized(
    api_client: ApiClient,
    competition: CreatedCompetition,
    update_competition_form_factory: UpdateCompetitionFormFactory,
) -> None:
    """Test updating competition fails when user is unauthorized."""
    data = update_competition_form_factory.build().model_dump(mode="json")

    response = await api_client.update_competition(competition.competition_id, data)

    response.assert_error(401, "UNAUTHORIZED")


async def test_update_competition_fails_if_not_owner(
    api_client: ApiClient,
    competition: CreatedCompetition,
    update_competition_form_factory: UpdateCompetitionFormFactory,
    different_organizer: CreatedOrganizer,  # noqa: ARG001
) -> None:
    """Test updating competition fails when user is not the owner."""
    data = update_competition_form_factory.build().model_dump(mode="json")

    with api_client.authenticate(auth_user_id=DIFFERENT_USER_ID):
        response = await api_client.update_competition(competition.competition_id, data)

    response.assert_error(403, "ACCESS_DENIED")


async def test_update_competition_fails_if_not_found(
    api_client: ApiClient,
    organizer: CreatedOrganizer,  # noqa: ARG001
    update_competition_form_factory: UpdateCompetitionFormFactory,
    faker: Faker,
) -> None:
    """Test updating competition fails when competition does not exist."""
    non_existent_id = faker.uuid4(cast_to=None)
    data = update_competition_form_factory.build().model_dump(mode="json")

    with api_client.authenticate(auth_user_id=USER_ID):
        response = await api_client.update_competition(non_existent_id, data)

    response.assert_error(404, "COMPETITION_NOT_FOUND")
