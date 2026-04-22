from datetime import UTC, datetime, timedelta
from typing import Any

import pytest

from dreamteams.entities.competition.schedule import ScheduleData
from tests.common.factory.competition import CompetitionFormFactory
from tests.common.helpers.competition import (
    INVALID_COMPETITION_DATA_CASES,
    milestones_from_deltas,
    schedule_from_deltas,
)
from tests.integration.api_client import ApiClient
from tests.integration.helpers.facade import Gateway


async def test_create_competition_as_organizer_succeeds(
    api_client: ApiClient,
    competition_form_factory: CompetitionFormFactory,
    gateway: Gateway,
) -> None:
    """Test creating competition as organizer."""
    organizer = await gateway.organizer.create_with_admin(gateway.admin)

    with api_client.authenticate(auth_user_id=organizer.organizer.auth_id):
        response = await api_client.create_competition(competition_form_factory.build().model_dump(mode="json"))

    response.assert_status(200).ensure_content()


async def test_create_competition_without_team_size_or_team_formation_succeeds(
    api_client: ApiClient,
    competition_form_factory: CompetitionFormFactory,
    gateway: Gateway,
) -> None:
    """Test creating competition without team_size and team_formation (both omitted together)."""
    # Arrange
    organizer = await gateway.organizer.create_with_admin(gateway.admin)
    now = datetime.now(tz=UTC)
    schedule = ScheduleData(
        registration_start=now + timedelta(days=1),
        registration_end=now + timedelta(days=10),
        team_formation_start=None,
        team_formation_end=None,
    )
    form = competition_form_factory.build(team_size=None, schedule=schedule)

    # Act
    with api_client.authenticate(auth_user_id=organizer.organizer.auth_id):
        response = await api_client.create_competition(form.model_dump(mode="json"))

    # Assert
    response.assert_status(200).ensure_content()


@pytest.mark.parametrize(("update_data", "expected_error"), INVALID_COMPETITION_DATA_CASES)
async def test_create_competition_with_invalid_data(
    api_client: ApiClient,
    competition_form_factory: CompetitionFormFactory,
    gateway: Gateway,
    update_data: dict[str, Any],
    expected_error: str,
) -> None:
    """Test creating competition with invalid data."""
    # Arrange
    organizer = await gateway.organizer.create_with_admin(gateway.admin)
    base_data = competition_form_factory.build().model_dump(mode="json")

    update_data = update_data.copy()
    if "schedule" in update_data:
        update_data["schedule"] = schedule_from_deltas(**update_data["schedule"])
    if "milestones" in update_data:
        update_data["milestones"] = milestones_from_deltas(update_data["milestones"])
    base_data.update(update_data)

    # Act
    with api_client.authenticate(auth_user_id=organizer.organizer.auth_id):
        response = await api_client.create_competition(base_data)

    # Assert
    response.assert_error(422, expected_error)


async def test_create_competition_fails_if_unauthorized(
    api_client: ApiClient,
    competition_form_factory: CompetitionFormFactory,
) -> None:
    """Test creating competition fails when user is unauthorized."""
    data = competition_form_factory.build().model_dump(mode="json")

    response = await api_client.create_competition(data)

    response.assert_error(401, "UNAUTHORIZED")
