from typing import Any

import pytest
from faker import Faker

from tests.common.factory.organizer import OrganizerFormFactory
from tests.integration.api_client import ApiClient
from tests.integration.conftest import DIFFERENT_USER_ID, USER_ID


async def test_register_as_organizer(
    api_client: ApiClient,
    organizer_form_factory: OrganizerFormFactory,
    faker: Faker,
) -> None:
    """Test register as organizer."""
    data = organizer_form_factory.build()

    with api_client.authenticate(auth_user_id=USER_ID, auth_user_email=faker.email()):
        response = await api_client.register_organizer(data.model_dump(mode="json"))

    response.assert_status(200).ensure_content()


@pytest.mark.parametrize(
    "update_data",
    [
        # Organizer name exceeds max length (100 characters)
        {"organizer_name": "a" * 101},
        # Phone number has invalid format
        {"phone_number": "aboba"},
        # Both name and phone are invalid
        {"organizer_name": "a" * 101, "phone_number": "aboba"},
    ],
)
async def test_register_as_organizer_with_invalid_data(
    api_client: ApiClient,
    organizer_form_factory: OrganizerFormFactory,
    update_data: dict[str, Any],
    faker: Faker,
) -> None:
    """Test register as organizer with invalid data."""
    data = organizer_form_factory.build().model_copy(update=update_data)

    with api_client.authenticate(auth_user_id=USER_ID, auth_user_email=faker.email()):
        response = await api_client.register_organizer(data.model_dump(mode="json"))

    response.assert_error(422, "VALIDATION_ERROR")


async def test_cannot_register_as_organizer_twice(
    api_client: ApiClient,
    organizer_form_factory: OrganizerFormFactory,
    faker: Faker,
) -> None:
    """Test that user cannot register as organizer when already registered as organizer."""
    data = organizer_form_factory.build()

    with api_client.authenticate(auth_user_id=USER_ID, auth_user_email=faker.email()):
        first_response = await api_client.register_organizer(data.model_dump(mode="json"))
        second_response = await api_client.register_organizer(data.model_dump(mode="json"))

    first_response.assert_status(200).ensure_content()
    second_response.assert_error(409, "ORGANIZER_ALREADY_EXISTS")


async def test_register_as_organizer_fails_if_unauthorized(
    api_client: ApiClient,
    organizer_form_factory: OrganizerFormFactory,
) -> None:
    """Test register as organizer fails when user unauthorized."""
    data = organizer_form_factory.build()

    response = await api_client.register_organizer(data.model_dump(mode="json"))

    response.assert_error(401, "UNAUTHORIZED")


@pytest.mark.parametrize(
    ("use_same_email", "use_same_phone"),
    [
        # Different users cannot register with same phone number
        (False, True),
        # Different users cannot register with same email
        (True, False),
        # Different users cannot register with both same email and phone number
        (True, True),
    ],
)
async def test_cannot_register_organizer_with_duplicate_contact_info(
    api_client: ApiClient,
    organizer_form_factory: OrganizerFormFactory,
    faker: Faker,
    email: str,
    use_same_email: bool,  # noqa: FBT001
    use_same_phone: bool,  # noqa: FBT001
) -> None:
    """Test that organizer cannot be registered with duplicate email or phone number."""
    first_data = organizer_form_factory.build()
    second_data = organizer_form_factory.build()

    if use_same_phone:
        second_data = second_data.model_copy(update={"phone_number": first_data.phone_number})

    first_email = email if use_same_email else faker.email()
    second_email = email if use_same_email else faker.email()

    with api_client.authenticate(auth_user_id=USER_ID, auth_user_email=first_email):
        first_response = await api_client.register_organizer(first_data.model_dump(mode="json"))
    with api_client.authenticate(auth_user_id=DIFFERENT_USER_ID, auth_user_email=second_email):
        second_response = await api_client.register_organizer(second_data.model_dump(mode="json"))

    first_response.assert_status(200).ensure_content()
    second_response.assert_error(409, "ORGANIZER_ALREADY_EXISTS")
