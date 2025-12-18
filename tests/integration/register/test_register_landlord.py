from typing import Any

import pytest
from faker import Faker

from tests.integration.api_client import ApiClient
from tests.integration.conftest import LandlordFormFactory


async def test_register_as_landlord(
    api_client: ApiClient,
    landlord_form_factory: LandlordFormFactory,
    faker: Faker,
) -> None:
    """Test register as landlord."""
    data = landlord_form_factory.build()

    with api_client.authenticate(auth_user_id="1", auth_user_email=faker.email()):
        response = await api_client.register_landlord(data)

    response.assert_status(200).ensure_ok()


@pytest.mark.parametrize(
    ("update_data"),
    [
        {
            "landlord_name": "a" * 100,
        },
        {
            "phone_number": "aboba",
        },
        {
            "landlord_name": "a" * 100,
            "phone_number": "aboba",
        },
    ],
)
async def test_register_as_landlord_with_invalid_data(
    api_client: ApiClient,
    landlord_form_factory: LandlordFormFactory,
    update_data: dict[str, Any],
    faker: Faker,
) -> None:
    """Test register as landlord witn invalid data."""
    data = landlord_form_factory.build().model_copy(update=update_data)

    with api_client.authenticate(auth_user_id="1", auth_user_email=faker.email()):
        response = await api_client.register_landlord(data)

    response.assert_error(422, "VALIDATION_ERROR")


async def test_register_as_landlord_by_multiple_users(
    api_client: ApiClient,
    landlord_form_factory: LandlordFormFactory,
    faker: Faker,
) -> None:
    """Test register as landlord by multiple users."""
    data = landlord_form_factory.build()

    with api_client.authenticate(auth_user_id="1", auth_user_email=faker.email()):
        first_response = await api_client.register_landlord(data)

    with api_client.authenticate(auth_user_id="2", auth_user_email=faker.email()):
        second_response = await api_client.register_landlord(data)

    first_content = first_response.assert_status(200).ensure_ok()
    second_content = second_response.assert_status(200).ensure_ok()

    assert first_content != second_content


async def test_cannot_register_as_landlord_twice(
    api_client: ApiClient,
    landlord_form_factory: LandlordFormFactory,
    faker: Faker,
) -> None:
    """Test register that user cannot register as landlord when already registered as landlord."""
    data = landlord_form_factory.build()

    with api_client.authenticate(auth_user_id="1", auth_user_email=faker.email()):
        first_response = await api_client.register_landlord(data)
        second_response = await api_client.register_landlord(data)

    first_response.assert_status(200).ensure_ok()
    second_response.assert_error(409, "AUTH_USER_ALREADY_EXISTS")


async def test_register_as_landlord_fails_if_unauthorized(
    api_client: ApiClient,
    landlord_form_factory: LandlordFormFactory,
) -> None:
    """Test register as landlord fails when user unauthorized."""
    data = landlord_form_factory.build()

    response = await api_client.register_landlord(data)

    response.assert_error(401, "UNAUTHORIZED")
