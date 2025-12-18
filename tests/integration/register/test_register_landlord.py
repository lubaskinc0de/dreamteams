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


async def test_register_as_landlord_fails_when_unauthorized(
    api_client: ApiClient,
    landlord_form_factory: LandlordFormFactory,
) -> None:
    """Test register as landlord fails when user unauthorized."""
    data = landlord_form_factory.build()

    response = await api_client.register_landlord(data)

    response.assert_error(401, "UNAUTHORIZED")
