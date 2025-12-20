from typing import Any

import pytest
from faker import Faker

from tests.integration.api_client import ApiClient
from tests.integration.conftest import OrganizerFormFactory


async def test_register_as_organizer(
    api_client: ApiClient,
    organizer_form_factory: OrganizerFormFactory,
    faker: Faker,
) -> None:
    """Test register as organizer."""
    data = organizer_form_factory.build()

    with api_client.authenticate(auth_user_id="1", auth_user_email=faker.email()):
        response = await api_client.register_organizer(data)

    response.assert_status(200).ensure_ok()


@pytest.mark.parametrize(
    ("update_data"),
    [
        {
            "organizer_name": "a" * 100,
        },
        {
            "phone_number": "aboba",
        },
        {
            "organizer_name": "a" * 100,
            "phone_number": "aboba",
        },
    ],
)
async def test_register_as_organizer_with_invalid_data(
    api_client: ApiClient,
    organizer_form_factory: OrganizerFormFactory,
    update_data: dict[str, Any],
    faker: Faker,
) -> None:
    """Test register as organizer witn invalid data."""
    data = organizer_form_factory.build().model_copy(update=update_data)

    with api_client.authenticate(auth_user_id="1", auth_user_email=faker.email()):
        response = await api_client.register_organizer(data)

    response.assert_error(422, "VALIDATION_ERROR")


async def test_cannot_register_as_organizer_twice(
    api_client: ApiClient,
    organizer_form_factory: OrganizerFormFactory,
    faker: Faker,
) -> None:
    """Test register that user cannot register as organizer when already registered as organizer."""
    data = organizer_form_factory.build()

    with api_client.authenticate(auth_user_id="1", auth_user_email=faker.email()):
        first_response = await api_client.register_organizer(data)
        second_response = await api_client.register_organizer(data)

    first_response.assert_status(200).ensure_ok()
    second_response.assert_error(409, "ORGANIZER_ALREADY_EXISTS")


async def test_register_as_organizer_fails_if_unauthorized(
    api_client: ApiClient,
    organizer_form_factory: OrganizerFormFactory,
) -> None:
    """Test register as organizer fails when user unauthorized."""
    data = organizer_form_factory.build()

    response = await api_client.register_organizer(data)

    response.assert_error(401, "UNAUTHORIZED")


async def test_cannot_register_organizer_with_same_phone_number(
    api_client: ApiClient,
    organizer_form_factory: OrganizerFormFactory,
    faker: Faker,
) -> None:
    """Test that organizer cannot be registered with the same phone number."""
    first_data = organizer_form_factory.build()
    second_data = organizer_form_factory.build().model_copy(update={"phone_number": first_data.phone_number})

    with api_client.authenticate(auth_user_id="1", auth_user_email=faker.email()):
        first_response = await api_client.register_organizer(first_data)
    with api_client.authenticate(auth_user_id="2", auth_user_email=faker.email()):
        second_response = await api_client.register_organizer(second_data)

    first_response.assert_status(200).ensure_ok()
    second_response.assert_error(409, "ORGANIZER_ALREADY_EXISTS")


async def test_cannot_register_organizer_with_same_email(
    api_client: ApiClient,
    organizer_form_factory: OrganizerFormFactory,
    email: str,
) -> None:
    """Test that organizer cannot be registered with the same email."""
    first_data = organizer_form_factory.build()
    second_data = organizer_form_factory.build()

    with api_client.authenticate(auth_user_id="1", auth_user_email=email):
        first_response = await api_client.register_organizer(first_data)
    with api_client.authenticate(auth_user_id="2", auth_user_email=email):
        second_response = await api_client.register_organizer(second_data)

    first_response.assert_status(200).ensure_ok()
    second_response.assert_error(409, "ORGANIZER_ALREADY_EXISTS")


async def test_cannot_register_organizer_with_same_phone_and_email(
    api_client: ApiClient,
    organizer_form_factory: OrganizerFormFactory,
    email: str,
) -> None:
    """Test that organizer cannot be registered with the same phone number and email."""
    first_data = organizer_form_factory.build()
    second_data = first_data.model_copy()

    with api_client.authenticate(auth_user_id="1", auth_user_email=email):
        first_response = await api_client.register_organizer(first_data)
    with api_client.authenticate(auth_user_id="2", auth_user_email=email):
        second_response = await api_client.register_organizer(second_data)

    first_response.assert_status(200).ensure_ok()
    second_response.assert_error(409, "ORGANIZER_ALREADY_EXISTS")
