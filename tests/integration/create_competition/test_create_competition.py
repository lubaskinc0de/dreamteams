from datetime import UTC, datetime, timedelta
from typing import Any

import pytest

from dreamteams.application.register.organizer import CreatedOrganizer
from tests.common.factory.competition import CompetitionFormFactory
from tests.integration.api_client import ApiClient


async def test_create_competition_as_organizer_succeeds(
    api_client: ApiClient,
    organizer: CreatedOrganizer,  # noqa: ARG001
    competition_form_factory: CompetitionFormFactory,
    email: str,
) -> None:
    """Test create competition as organizer."""
    data = competition_form_factory.build().model_dump(mode="json")

    with api_client.authenticate(auth_user_id="1", auth_user_email=email):
        response = await api_client.create_competition(data)

    response.assert_status(200).ensure_ok()


@pytest.mark.parametrize(
    ("update_data", "expected_error"),
    [
        # ({"title": "a" * 300}, "VALIDATION_ERROR"),
        # ({"description": ""}, "INVALID_COMPETITION_DATA"),
        # ({"description": "   "}, "INVALID_COMPETITION_DATA"),
        # ({"domains": []}, "INVALID_COMPETITION_DATA"),
        # (
        #     {
        #         "schedule": {
        #             "competition_start": (datetime.now(tz=UTC) + timedelta(days=10)).isoformat(),
        #             "competition_end": (datetime.now(tz=UTC) + timedelta(days=20)).isoformat(),
        #             "registration_start": (datetime.now(tz=UTC) + timedelta(days=5)).isoformat(),
        #             "registration_end": (datetime.now(tz=UTC) + timedelta(days=15)).isoformat(),
        #         },
        #     },
        #     "INVALID_COMPETITION_DATA",
        # ),
        # (
        #     {
        #         "schedule": {
        #             "competition_start": (datetime.now(tz=UTC) + timedelta(days=10)).isoformat(),
        #             "competition_end": (datetime.now(tz=UTC) + timedelta(days=1)).isoformat(),
        #             "registration_start": (datetime.now(tz=UTC) + timedelta(days=1)).isoformat(),
        #             "registration_end": (datetime.now(tz=UTC) + timedelta(days=5)).isoformat(),
        #         },
        #     },
        #     "INVALID_COMPETITION_DATA",
        # ),
        # (
        #     {
        #         "schedule": {
        #             "competition_start": (datetime.now(tz=UTC) - timedelta(days=10)).isoformat(),
        #             "competition_end": (datetime.now(tz=UTC) + timedelta(days=1)).isoformat(),
        #             "registration_start": (datetime.now(tz=UTC) - timedelta(days=15)).isoformat(),
        #             "registration_end": (datetime.now(tz=UTC) - timedelta(days=11)).isoformat(),
        #         },
        #     },
        #     "INVALID_COMPETITION_DATA",
        # ),
        # ({"participant_limits": {"max": 10, "min": 50}}, "INVALID_COMPETITION_DATA"),
        # ({"participant_limits": {"max": 0, "min": 0}}, "INVALID_COMPETITION_DATA"),
        # ({"team_size": {"max": 3, "min": 10}}, "INVALID_COMPETITION_DATA"),
        # ({"team_size": {"max": 0, "min": 1}}, "INVALID_COMPETITION_DATA"),
        # ({"team_size": {"max": 5, "min": 0}}, "INVALID_COMPETITION_DATA"),
        # ({"participant_limits": {"max": 100, "min": -10}}, "INVALID_COMPETITION_DATA"), 
        ( # problem
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
        ({"venue": {"format": "offline", "location": ""}}, "INVALID_COMPETITION_DATA"),
        ({"venue": {"format": "offline", "location": "   "}}, "INVALID_COMPETITION_DATA"),
        ({"venue": {"format": "hybrid", "location": ""}}, "INVALID_COMPETITION_DATA"),
        ({"venue": {"format": "hybrid", "location": "   "}}, "INVALID_COMPETITION_DATA"),
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
    """Test create competition with invalid data."""
    base_data = competition_form_factory.build().model_dump(mode="json")
    base_data.update(update_data)

    with api_client.authenticate(auth_user_id="1", auth_user_email=email):
        response = await api_client.create_competition(base_data)

    response.assert_error(422, expected_error)


async def test_create_competition_fails_if_unauthorized(
    api_client: ApiClient,
    competition_form_factory: CompetitionFormFactory,
) -> None:
    """Test create competition fails when user unauthorized."""
    data = competition_form_factory.build().model_dump(mode="json")

    response = await api_client.create_competition(data)

    response.assert_error(401, "UNAUTHORIZED")
