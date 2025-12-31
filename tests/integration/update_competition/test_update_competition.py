from typing import Any

import pytest
from faker import Faker

from dreamteams.application.create_competition.interactor import CreatedCompetition
from dreamteams.application.register.organizer import CreatedOrganizer
from tests.common.factory.competition import UpdateCompetitionFormFactory
from tests.common.factory.organizer import OrganizerFormFactory
from tests.integration.api_client import ApiClient
from tests.integration.conftest import INVALID_COMPETITION_DATA_CASES, schedule_from_deltas

# Test user ID for authentication
USER_ID = "1"


async def test_update_competition_as_owner_succeeds(
    api_client: ApiClient,
    competition: CreatedCompetition,
    update_competition_form_factory: UpdateCompetitionFormFactory,
    email: str,
) -> None:
    """Test updating competition as owner."""
    data = update_competition_form_factory.build().model_dump(mode="json")

    with api_client.authenticate(auth_user_id=USER_ID, auth_user_email=email):
        response = await api_client.update_competition(competition.competition_id, data)

    response.assert_status(200)


@pytest.mark.parametrize(("update_data", "expected_error"), INVALID_COMPETITION_DATA_CASES)
async def test_update_competition_with_invalid_data(
    api_client: ApiClient,
    competition: CreatedCompetition,
    update_competition_form_factory: UpdateCompetitionFormFactory,
    update_data: dict[str, Any],
    expected_error: str,
) -> None:
    """Test updating competition with invalid data."""
    base_data = update_competition_form_factory.build().model_dump(mode="json")

    # Make a copy to avoid modifying the shared constant
    update_data = update_data.copy()

    # Convert schedule with timedelta to ISO strings
    if "schedule" in update_data:
        schedule = update_data["schedule"]
        update_data["schedule"] = schedule_from_deltas(**schedule)

    base_data.update(update_data)

    with api_client.authenticate(auth_user_id=USER_ID):
        response = await api_client.update_competition(competition.competition_id, base_data)

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
    organizer_form_factory: OrganizerFormFactory,
    faker: Faker,
) -> None:
    """Test updating competition fails when user is not the owner."""
    data = update_competition_form_factory.build().model_dump(mode="json")
    second_organizer_data = organizer_form_factory.build()
    second_organizer_email = faker.email()

    with api_client.authenticate(auth_user_id="999", auth_user_email=second_organizer_email):
        (await api_client.register_organizer(second_organizer_data.model_dump(mode="json"))).assert_status(200)
        response = await api_client.update_competition(competition.competition_id, data)

    response.assert_error(403, "ACCESS_DENIED")


async def test_update_competition_fails_if_not_found(
    api_client: ApiClient,
    organizer: CreatedOrganizer,  # noqa: ARG001
    update_competition_form_factory: UpdateCompetitionFormFactory,
    email: str,
    faker: Faker,
) -> None:
    """Test updating competition fails when competition does not exist."""
    non_existent_id = faker.uuid4(cast_to=None)
    data = update_competition_form_factory.build().model_dump(mode="json")

    with api_client.authenticate(auth_user_id=USER_ID, auth_user_email=email):
        response = await api_client.update_competition(non_existent_id, data)

    response.assert_error(404, "COMPETITION_NOT_FOUND")
