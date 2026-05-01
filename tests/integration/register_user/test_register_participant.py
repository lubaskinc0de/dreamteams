from typing import Any
from uuid import uuid4

import pytest
from faker import Faker

from dreamteams.application.common.dto.participant_contact import MAX_CONTACT_VALUE_LENGTH, ParticipantContactForm
from dreamteams.application.common.dto.participant_skill import MAX_PARTICIPANT_SKILLS, ParticipantSkillForm
from dreamteams.entities.participant.participant_contact import ParticipantContact
from dreamteams.entities.participant.participant_skill import SkillLevel
from tests.common.factory.participant import ParticipantFormFactory
from tests.integration.api_client import ApiClient


async def test_register_as_participant(
    api_client: ApiClient,
    participant_form_factory: ParticipantFormFactory,
    faker: Faker,
) -> None:
    """Test register as participant."""
    data = {**participant_form_factory.build().model_dump(mode="json")}

    with api_client.authenticate(auth_user_id=str(uuid4()), auth_user_email=faker.email()):
        response = await api_client.register_participant(data=data)

    response.assert_status(200).ensure_content()


async def test_register_as_participant_without_optional_fields(
    api_client: ApiClient,
    participant_form_factory: ParticipantFormFactory,
    faker: Faker,
) -> None:
    """Test register as participant succeeds when all optional fields are omitted."""
    data = participant_form_factory.build(
        bio=None,
        skills=[],
        experience_level=None,
        contacts=[],
    ).model_dump(mode="json")

    with api_client.authenticate(auth_user_id=str(uuid4()), auth_user_email=faker.email()):
        response = await api_client.register_participant(data=data)

    response.assert_status(200).ensure_content()


async def test_register_as_participant_adds_auth_email_to_contacts(
    api_client: ApiClient,
    participant_form_factory: ParticipantFormFactory,
    faker: Faker,
) -> None:
    """Registering as participant adds the auth email as an Email contact."""
    # Arrange
    auth_user_id = str(uuid4())
    auth_user_email = faker.email()
    data = participant_form_factory.build(contacts=[]).model_dump(mode="json", exclude={"email"})

    # Act
    with api_client.authenticate(auth_user_id=auth_user_id, auth_user_email=auth_user_email):
        register_response = await api_client.register_participant(data=data)
        profile_response = await api_client.view_profile()

    # Assert
    register_response.assert_status(200).ensure_content()
    profile = profile_response.assert_status(200).ensure_content()
    assert profile.participant is not None
    assert profile.participant.contacts == [ParticipantContact(title="Email", value=auth_user_email)]


async def test_register_as_participant_without_auth_email_does_not_add_email_contact(
    api_client: ApiClient,
    participant_form_factory: ParticipantFormFactory,
) -> None:
    """Registering as participant without auth email keeps contacts unchanged."""
    # Arrange
    auth_user_id = str(uuid4())
    data = participant_form_factory.build(contacts=[]).model_dump(mode="json", exclude={"email"})

    # Act
    with api_client.authenticate(auth_user_id=auth_user_id):
        register_response = await api_client.register_participant(data=data)
        profile_response = await api_client.view_profile()

    # Assert
    register_response.assert_status(200).ensure_content()
    profile = profile_response.assert_status(200).ensure_content()
    assert profile.participant is not None
    assert profile.participant.contacts == []


async def test_register_participant_rejects_more_than_fifteen_contacts(
    api_client: ApiClient,
    participant_form_factory: ParticipantFormFactory,
    faker: Faker,
) -> None:
    """Registering a participant with more than 15 contacts is rejected by request validation."""
    # Arrange
    data = participant_form_factory.build().model_dump(mode="json")
    data["contacts"] = [{"title": f"contact-{i}", "value": f"https://example.com/{i}"} for i in range(16)]

    # Act
    with api_client.authenticate(auth_user_id=str(uuid4()), auth_user_email=faker.email()):
        response = await api_client.register_participant(data=data)

    # Assert
    response.assert_error(422, "VALIDATION_ERROR")


async def test_register_participant_rejects_too_many_skills(
    api_client: ApiClient,
    participant_form_factory: ParticipantFormFactory,
    faker: Faker,
) -> None:
    """Registering a participant with too many skills is rejected by request validation."""
    # Arrange
    data = participant_form_factory.build().model_copy(
        update={
            "skills": [
                ParticipantSkillForm(name=f"skill-{i}", level=SkillLevel.BEGINNER)
                for i in range(MAX_PARTICIPANT_SKILLS + 1)
            ],
        },
    )

    # Act
    with api_client.authenticate(auth_user_id=str(uuid4()), auth_user_email=faker.email()):
        response = await api_client.register_participant(data=data.model_dump(mode="json"))

    # Assert
    response.assert_error(422, "VALIDATION_ERROR")


async def test_register_participant_rejects_too_long_contact_value(
    api_client: ApiClient,
    participant_form_factory: ParticipantFormFactory,
    faker: Faker,
) -> None:
    """Registering a participant with an oversized contact value is rejected by request validation."""
    # Arrange
    data = participant_form_factory.build().model_copy(
        update={
            "contacts": [
                ParticipantContactForm.model_construct(
                    title="Telegram",
                    value="a" * (MAX_CONTACT_VALUE_LENGTH + 1),
                ),
            ],
        },
    )

    # Act
    with api_client.authenticate(auth_user_id=str(uuid4()), auth_user_email=faker.email()):
        response = await api_client.register_participant(data=data.model_dump(mode="json"))

    # Assert
    response.assert_error(422, "VALIDATION_ERROR")


@pytest.mark.parametrize(
    "update_data",
    [
        # Participant full name exceeds max length (70 characters)
        {"full_name": "a" * 71},
        # Participant bio exceeds max length (500 characters)
        {"bio": "a" * 501},
        # Malformed skill object (empty name, invalid level)
        {"skills": [{"name": "", "level": ""}]},
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
    data = participant_form_factory.build().model_dump(mode="json")
    data.update(update_data)

    with api_client.authenticate(auth_user_id=str(uuid4()), auth_user_email=faker.email()):
        response = await api_client.register_participant(data)

    response.assert_error(422, "VALIDATION_ERROR")


@pytest.mark.parametrize("age", [-1, 151])
async def test_register_as_participant_with_invalid_age(
    api_client: ApiClient,
    participant_form_factory: ParticipantFormFactory,
    age: int,
    faker: Faker,
) -> None:
    """Test register as participant fails when age is out of bounds."""
    data = participant_form_factory.build().model_copy(update={"age": age})

    with api_client.authenticate(auth_user_id=str(uuid4()), auth_user_email=faker.email()):
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
