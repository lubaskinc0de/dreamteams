from typing import Any

import pytest
from faker import Faker

from tests.common.factory.participant import ParticipantFormFactory
from tests.integration.api_client import ApiClient
from tests.integration.constants import USER_ID


async def test_register_as_participant(
    api_client: ApiClient,
    participant_form_factory: ParticipantFormFactory,
    faker: Faker,
) -> None:
    """Test register as participant."""
    data = {**participant_form_factory.build().model_dump(mode="json")}

    with api_client.authenticate(auth_user_id=USER_ID, auth_user_email=faker.email()):
        response = await api_client.register_participant(data=data)

    response.assert_status(200).ensure_content()


@pytest.mark.parametrize(
    "update_data",
    [
        # Participant full name exceeds max length (70 characters)
        {"full_name": "a" * 71},
        # Participant bio exceeds max length (500 characters)
        {"bio": "a" * 501},
        # Participant skills empty
        {"skills": [{"name": "", "level": ""}]},
        # Incorrect contact url
        {"contacts": [{"title": "GitHub", "url": "not-a-url"}]},
        # Both full name and skills are invalid
        {"full_name": "a" * 71, "skills": [{"name": "", "level": ""}]},
    ],
)
async def test_register_as_participant_with_invalid_data(
    api_client: ApiClient,
    participant_form_factory: ParticipantFormFactory,
    update_data: dict[str, Any],
    faker: Faker,
) -> None:
    """Test register as participant with invalid data."""
    data = participant_form_factory.build().model_copy(update=update_data)

    with api_client.authenticate(auth_user_id=USER_ID, auth_user_email=faker.email()):
        response = await api_client.register_participant(data.model_dump(mode="json"))

    response.assert_error(422, "VALIDATION_ERROR")


async def test_register_as_participant_fails_if_unauthorized(
    api_client: ApiClient,
    participant_form_factory: ParticipantFormFactory,
) -> None:
    """Test register as participant fails when user unauthorized."""
    data = participant_form_factory.build()

    response = await api_client.register_participant(data.model_dump(mode="json"))

    response.assert_error(401, "UNAUTHORIZED")
