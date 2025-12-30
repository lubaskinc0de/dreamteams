from datetime import UTC, datetime, timedelta
from typing import Any

import pytest

from dreamteams.application.register.organizer import CreatedOrganizer
from tests.common.factory.competition import CompetitionFormFactory
from tests.integration.api_client import ApiClient

# Test user ID for authentication
USER_ID = "1"


async def test_create_competition_as_organizer_succeeds(
    api_client: ApiClient,
    organizer: CreatedOrganizer,  # noqa: ARG001
    competition_form_factory: CompetitionFormFactory,
    email: str,
) -> None:
    """Test creating competition as organizer."""
    data = competition_form_factory.build().model_dump(mode="json")

    with api_client.authenticate(auth_user_id=USER_ID, auth_user_email=email):
        response = await api_client.create_competition(data)

    response.assert_status(200).ensure_content()


@pytest.mark.parametrize(
    ("update_data", "expected_error"),
    [
        # Title validation
        ({"title": "a" * 300}, "VALIDATION_ERROR"),  # Title exceeds max length (200 characters)
        # Description validation
        ({"description": ""}, "INVALID_COMPETITION_DATA"),  # Description cannot be empty
        ({"description": "   "}, "INVALID_COMPETITION_DATA"),  # Description cannot be whitespace only
        # Domains validation
        ({"domains": []}, "INVALID_COMPETITION_DATA"),  # Domains list cannot be empty
        # Schedule validation: registration end after competition start
        (
            {
                "schedule": {
                    "competition_start": (datetime.now(tz=UTC) + timedelta(days=10)).isoformat(),
                    "competition_end": (datetime.now(tz=UTC) + timedelta(days=20)).isoformat(),
                    "registration_start": (datetime.now(tz=UTC) + timedelta(days=5)).isoformat(),
                    "registration_end": (datetime.now(tz=UTC) + timedelta(days=15)).isoformat(),
                },
            },
            "INVALID_COMPETITION_DATA",
        ),
        # Schedule validation: competition end before competition start
        (
            {
                "schedule": {
                    "competition_start": (datetime.now(tz=UTC) + timedelta(days=10)).isoformat(),
                    "competition_end": (datetime.now(tz=UTC) + timedelta(days=1)).isoformat(),
                    "registration_start": (datetime.now(tz=UTC) + timedelta(days=1)).isoformat(),
                    "registration_end": (datetime.now(tz=UTC) + timedelta(days=5)).isoformat(),
                },
            },
            "INVALID_COMPETITION_DATA",
        ),
        # Schedule validation: dates in the past
        (
            {
                "schedule": {
                    "competition_start": (datetime.now(tz=UTC) - timedelta(days=10)).isoformat(),
                    "competition_end": (datetime.now(tz=UTC) + timedelta(days=1)).isoformat(),
                    "registration_start": (datetime.now(tz=UTC) - timedelta(days=15)).isoformat(),
                    "registration_end": (datetime.now(tz=UTC) - timedelta(days=11)).isoformat(),
                },
            },
            "INVALID_COMPETITION_DATA",
        ),
        # Participant limits: min exceeds max
        ({"participant_limits": {"max": 10, "min": 50}}, "INVALID_COMPETITION_DATA"),
        # Participant limits: both zero
        ({"participant_limits": {"max": 0, "min": 0}}, "INVALID_COMPETITION_DATA"),
        # Team size: min exceeds max
        ({"team_size": {"max": 3, "min": 10}}, "INVALID_COMPETITION_DATA"),
        # Team size: max is zero
        ({"team_size": {"max": 0, "min": 1}}, "INVALID_COMPETITION_DATA"),
        # Team size: min is zero (must be at least 1)
        ({"team_size": {"max": 5, "min": 0}}, "INVALID_COMPETITION_DATA"),
        # Participant limits: negative min
        ({"participant_limits": {"max": 100, "min": -10}}, "INVALID_COMPETITION_DATA"),
        # Schedule validation: competition start equals competition end
        (
            {
                "schedule": {
                    "competition_start": (datetime.now(tz=UTC) + timedelta(days=10)).isoformat(),
                    "competition_end": (datetime.now(tz=UTC) + timedelta(days=10)).isoformat(),
                    "registration_start": (datetime.now(tz=UTC) + timedelta(days=1)).isoformat(),
                    "registration_end": (datetime.now(tz=UTC) + timedelta(days=5)).isoformat(),
                },
            },
            "INVALID_COMPETITION_DATA",
        ),
        # Schedule validation: registration start equals registration end
        (
            {
                "schedule": {
                    "competition_start": (datetime.now(tz=UTC) + timedelta(days=10)).isoformat(),
                    "competition_end": (datetime.now(tz=UTC) + timedelta(days=20)).isoformat(),
                    "registration_start": (datetime.now(tz=UTC) + timedelta(days=5)).isoformat(),
                    "registration_end": (datetime.now(tz=UTC) + timedelta(days=5)).isoformat(),
                },
            },
            "INVALID_COMPETITION_DATA",
        ),
        # Venue: offline format requires location
        ({"venue": {"format": "offline", "location": ""}}, "INVALID_COMPETITION_DATA"),
        ({"venue": {"format": "offline", "location": "   "}}, "INVALID_COMPETITION_DATA"),
        # Venue: hybrid format requires location
        ({"venue": {"format": "hybrid", "location": ""}}, "INVALID_COMPETITION_DATA"),
        ({"venue": {"format": "hybrid", "location": "   "}}, "INVALID_COMPETITION_DATA"),
        # Team formation: only start specified (both must be specified together)
        (
            {
                "schedule": {
                    "competition_start": (datetime.now(tz=UTC) + timedelta(days=11)).isoformat(),
                    "competition_end": (datetime.now(tz=UTC) + timedelta(days=15)).isoformat(),
                    "registration_start": (datetime.now(tz=UTC) + timedelta(days=1)).isoformat(),
                    "registration_end": (datetime.now(tz=UTC) + timedelta(days=10)).isoformat(),
                    "team_formation_start": (datetime.now(tz=UTC) + timedelta(days=11)).isoformat(),
                },
            },
            "INVALID_COMPETITION_DATA",
        ),
        # Team formation: only end specified (both must be specified together)
        (
            {
                "schedule": {
                    "competition_start": (datetime.now(tz=UTC) + timedelta(days=11)).isoformat(),
                    "competition_end": (datetime.now(tz=UTC) + timedelta(days=15)).isoformat(),
                    "registration_start": (datetime.now(tz=UTC) + timedelta(days=1)).isoformat(),
                    "registration_end": (datetime.now(tz=UTC) + timedelta(days=10)).isoformat(),
                    "team_formation_end": (datetime.now(tz=UTC) + timedelta(days=12)).isoformat(),
                },
            },
            "INVALID_COMPETITION_DATA",
        ),
        # Team formation: starts before registration end
        (
            {
                "schedule": {
                    "competition_start": (datetime.now(tz=UTC) + timedelta(days=11)).isoformat(),
                    "competition_end": (datetime.now(tz=UTC) + timedelta(days=15)).isoformat(),
                    "registration_start": (datetime.now(tz=UTC) + timedelta(days=1)).isoformat(),
                    "registration_end": (datetime.now(tz=UTC) + timedelta(days=10)).isoformat(),
                    "team_formation_start": (datetime.now(tz=UTC) + timedelta(days=9)).isoformat(),
                    "team_formation_end": (datetime.now(tz=UTC) + timedelta(days=12)).isoformat(),
                },
            },
            "INVALID_COMPETITION_DATA",
        ),
        # Team formation: ends after competition end
        (
            {
                "schedule": {
                    "competition_start": (datetime.now(tz=UTC) + timedelta(days=11)).isoformat(),
                    "competition_end": (datetime.now(tz=UTC) + timedelta(days=15)).isoformat(),
                    "registration_start": (datetime.now(tz=UTC) + timedelta(days=1)).isoformat(),
                    "registration_end": (datetime.now(tz=UTC) + timedelta(days=10)).isoformat(),
                    "team_formation_start": (datetime.now(tz=UTC) + timedelta(days=11)).isoformat(),
                    "team_formation_end": (datetime.now(tz=UTC) + timedelta(days=16)).isoformat(),
                },
            },
            "INVALID_COMPETITION_DATA",
        ),
    ],
)
async def test_create_competition_with_invalid_data(
    api_client: ApiClient,
    organizer: CreatedOrganizer,  # noqa: ARG001
    competition_form_factory: CompetitionFormFactory,
    update_data: dict[str, Any],
    expected_error: str,
    email: str,
) -> None:
    """Test creating competition with invalid data."""
    base_data = competition_form_factory.build().model_dump(mode="json")
    base_data.update(update_data)

    with api_client.authenticate(auth_user_id=USER_ID, auth_user_email=email):
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
