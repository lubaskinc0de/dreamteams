from typing import Any

import pytest
from faker import Faker

from dreamteams.application.manage_invites import InviteIssued
from dreamteams.entities.common.identifiers import UserId
from tests.common.factory.organizer import OrganizerFormFactory
from tests.integration.api_client import ApiClient
from tests.integration.constants import ADMIN_USER_ID, DIFFERENT_USER_ID, USER_ID


async def test_register_as_organizer(
    api_client: ApiClient,
    organizer_form_factory: OrganizerFormFactory,
    faker: Faker,
    issued_invite: InviteIssued,
    admin_user_id: UserId,  # noqa: ARG001
) -> None:
    """Test register as organizer."""
    data = {**organizer_form_factory.build().model_dump(mode="json"), "invite_code": issued_invite.code}

    with api_client.authenticate(auth_user_id=USER_ID, auth_user_email=faker.email()):
        response = await api_client.register_organizer(data)

    response.assert_status(200).ensure_content()


@pytest.mark.parametrize(
    "update_data",
    [
        # Organizer name exceeds max length (70 characters)
        {"organizer_name": "a" * 71},
        # Phone number has invalid format
        {"phone_number": "aboba"},
        # Both name and phone are invalid
        {"organizer_name": "a" * 71, "phone_number": "aboba"},
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
    admin_user_id: UserId,  # noqa: ARG001
) -> None:
    """Test that user cannot register as organizer when already registered as organizer."""
    with api_client.authenticate(auth_user_id=ADMIN_USER_ID):
        invite1_resp = await api_client.issue_invite({})
        invite2_resp = await api_client.issue_invite({})
    invite1 = invite1_resp.assert_status(200).ensure_content()
    invite2 = invite2_resp.assert_status(200).ensure_content()

    email = faker.email()
    data1 = {**organizer_form_factory.build().model_dump(mode="json"), "invite_code": invite1.code}
    data2 = {**organizer_form_factory.build().model_dump(mode="json"), "invite_code": invite2.code}

    with api_client.authenticate(auth_user_id=USER_ID, auth_user_email=email):
        first_response = await api_client.register_organizer(data1)
        second_response = await api_client.register_organizer(data2)

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
    admin_user_id: UserId,  # noqa: ARG001
    use_same_email: bool,  # noqa: FBT001
    use_same_phone: bool,  # noqa: FBT001
) -> None:
    """Test that organizer cannot be registered with duplicate email or phone number."""
    with api_client.authenticate(auth_user_id=ADMIN_USER_ID):
        invite1_resp = await api_client.issue_invite({})
        invite2_resp = await api_client.issue_invite({})
    invite1 = invite1_resp.assert_status(200).ensure_content()
    invite2 = invite2_resp.assert_status(200).ensure_content()

    first_data = organizer_form_factory.build()
    second_data = organizer_form_factory.build()
    if use_same_phone:
        second_data = second_data.model_copy(update={"phone_number": first_data.phone_number})
    first_email = email if use_same_email else faker.email()
    second_email = email if use_same_email else faker.email()

    with api_client.authenticate(auth_user_id=USER_ID, auth_user_email=first_email):
        first_response = await api_client.register_organizer(
            {**first_data.model_dump(mode="json"), "invite_code": invite1.code},
        )
    with api_client.authenticate(auth_user_id=DIFFERENT_USER_ID, auth_user_email=second_email):
        second_response = await api_client.register_organizer(
            {**second_data.model_dump(mode="json"), "invite_code": invite2.code},
        )

    first_response.assert_status(200).ensure_content()
    second_response.assert_error(409, "ORGANIZER_ALREADY_EXISTS")


async def test_register_with_nonexistent_invite_code_fails(
    api_client: ApiClient,
    organizer_form_factory: OrganizerFormFactory,
    faker: Faker,
) -> None:
    """Registering with a nonexistent invite code fails with INVITE_NOT_FOUND."""
    data = {**organizer_form_factory.build().model_dump(mode="json"), "invite_code": "nonexistent-code"}

    with api_client.authenticate(auth_user_id=USER_ID, auth_user_email=faker.email()):
        response = await api_client.register_organizer(data)

    response.assert_error(404, "INVITE_NOT_FOUND")


async def test_register_with_revoked_invite_code_fails(
    api_client: ApiClient,
    organizer_form_factory: OrganizerFormFactory,
    faker: Faker,
    issued_invite: InviteIssued,
    admin_user_id: UserId,  # noqa: ARG001
) -> None:
    """Registering with a revoked invite code fails with INVITE_REVOKED."""
    with api_client.authenticate(auth_user_id=ADMIN_USER_ID):
        await api_client.revoke_invite(issued_invite.invite_id)

    data = {**organizer_form_factory.build().model_dump(mode="json"), "invite_code": issued_invite.code}

    with api_client.authenticate(auth_user_id=USER_ID, auth_user_email=faker.email()):
        response = await api_client.register_organizer(data)

    response.assert_error(403, "INVITE_REVOKED")


async def test_register_with_used_invite_code_fails(
    api_client: ApiClient,
    organizer_form_factory: OrganizerFormFactory,
    faker: Faker,
    issued_invite: InviteIssued,
    admin_user_id: UserId,  # noqa: ARG001
) -> None:
    """Registering with an already-used invite code fails with INVITE_ALREADY_USED."""
    data = {**organizer_form_factory.build().model_dump(mode="json"), "invite_code": issued_invite.code}

    with api_client.authenticate(auth_user_id=USER_ID, auth_user_email=faker.email()):
        await api_client.register_organizer(data)

    second_data = {**organizer_form_factory.build().model_dump(mode="json"), "invite_code": issued_invite.code}

    with api_client.authenticate(auth_user_id=DIFFERENT_USER_ID, auth_user_email=faker.email()):
        response = await api_client.register_organizer(second_data)

    response.assert_error(409, "INVITE_ALREADY_USED")
