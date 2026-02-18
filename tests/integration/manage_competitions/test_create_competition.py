from typing import Any

import pytest

from dreamteams.application.register.register_organizer import CreatedOrganizer
from tests.common.factory.competition import CompetitionFormFactory
from tests.common.helpers.competition import (
    INVALID_COMPETITION_DATA_CASES,
    milestones_from_deltas,
    schedule_from_deltas,
)
from tests.integration.api_client import ApiClient
from tests.integration.constants import USER_ID


async def test_create_competition_as_organizer_succeeds(
    api_client: ApiClient,
    organizer: CreatedOrganizer,  # noqa: ARG001
    competition_form_factory: CompetitionFormFactory,
) -> None:
    """Test creating competition as organizer."""
    data = competition_form_factory.build().model_dump(mode="json")

    with api_client.authenticate(auth_user_id=USER_ID):
        response = await api_client.create_competition(data)

    response.assert_status(200).ensure_content()


@pytest.mark.parametrize(("update_data", "expected_error"), INVALID_COMPETITION_DATA_CASES)
async def test_create_competition_with_invalid_data(
    api_client: ApiClient,
    organizer: CreatedOrganizer,  # noqa: ARG001
    competition_form_factory: CompetitionFormFactory,
    update_data: dict[str, Any],
    expected_error: str,
) -> None:
    """Test creating competition with invalid data."""
    base_data = competition_form_factory.build().model_dump(mode="json")

    update_data = update_data.copy()

    # Convert schedule with timedelta to ISO strings
    if "schedule" in update_data:
        schedule = update_data["schedule"]
        update_data["schedule"] = schedule_from_deltas(**schedule)

    # Convert milestones with timedelta to ISO strings
    if "milestones" in update_data:
        update_data["milestones"] = milestones_from_deltas(update_data["milestones"])

    base_data.update(update_data)

    with api_client.authenticate(auth_user_id=USER_ID):
        response = await api_client.create_competition(base_data)

    response.assert_error(422, expected_error)


async def test_create_competition_fails_if_unauthorized(
    api_client: ApiClient,
    competition_form_factory: CompetitionFormFactory,
) -> None:
    """Test creating competition fails when user is unauthorized."""
    data = competition_form_factory.build().model_dump(mode="json")

    response = await api_client.create_competition(data)

    response.assert_error(401, "UNAUTHORIZED")
