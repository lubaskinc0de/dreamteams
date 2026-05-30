import asyncio
from typing import Any
from uuid import uuid4

import pytest
from faker import Faker

from dreamteams.application.register_user.register_organizer import MAX_INVITE_CODE_LENGTH, CreatedOrganizer
from tests.common.factory.organizer import OrganizerFormFactory
from tests.integration.api_client import ApiClient, APIResponse
from tests.integration.helpers.facade import Gateway
from tests.integration.helpers.race import assert_one_success_one_error

_ORGANIZER_UNIQUENESS_RACE_ERRORS = frozenset(
    {
        (409, "ORGANIZER_ALREADY_EXISTS"),
        (429, "INTEGRITY_CONFLICT"),
    },
)


async def test_register_as_organizer(gateway: Gateway) -> None:
    """Test register as organizer."""
    organizer = await gateway.organizer.create_with_admin(gateway.admin)

    assert organizer.organizer.created.user_id is not None


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

    with api_client.authenticate(auth_user_id=str(uuid4()), auth_user_email=faker.email()):
        response = await api_client.register_organizer(data.model_dump(mode="json"))

    response.assert_error(422, "VALIDATION_ERROR")


async def test_cannot_register_as_organizer_twice(
    api_client: ApiClient,
    organizer_form_factory: OrganizerFormFactory,
    faker: Faker,
    gateway: Gateway,
) -> None:
    """Test that user cannot register as organizer when already registered as organizer."""
    # Arrange
    admin = await gateway.admin.create()
    with api_client.authenticate(auth_user_id=admin.auth_id):
        invite1 = (await api_client.issue_invite({})).assert_status(200).ensure_content()
        invite2 = (await api_client.issue_invite({})).assert_status(200).ensure_content()

    organizer_auth_id = str(uuid4())
    email = faker.email()

    # Act
    with api_client.authenticate(auth_user_id=organizer_auth_id, auth_user_email=email):
        first_response = await api_client.register_organizer(
            organizer_form_factory.build(invite_code=invite1.code).model_dump(mode="json"),
        )
        second_response = await api_client.register_organizer(
            organizer_form_factory.build(invite_code=invite2.code).model_dump(mode="json"),
        )

    # Assert
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


async def test_cannot_register_two_organizers_with_same_email(
    api_client: ApiClient,
    organizer_form_factory: OrganizerFormFactory,
    faker: Faker,
    gateway: Gateway,
) -> None:
    """Two different users cannot register as organizers with the same email."""
    # Arrange
    admin = await gateway.admin.create()
    with api_client.authenticate(auth_user_id=admin.auth_id):
        invite1 = (await api_client.issue_invite({})).assert_status(200).ensure_content()
        invite2 = (await api_client.issue_invite({})).assert_status(200).ensure_content()

    shared_email = faker.email()

    # Act
    with api_client.authenticate(auth_user_id=str(uuid4()), auth_user_email=shared_email):
        first_response = await api_client.register_organizer(
            organizer_form_factory.build(invite_code=invite1.code).model_dump(mode="json"),
        )
    with api_client.authenticate(auth_user_id=str(uuid4()), auth_user_email=shared_email):
        second_response = await api_client.register_organizer(
            organizer_form_factory.build(invite_code=invite2.code).model_dump(mode="json"),
        )

    # Assert
    first_response.assert_status(200).ensure_content()
    second_response.assert_error(409, "ORGANIZER_ALREADY_EXISTS")


async def test_cannot_register_two_organizers_with_same_phone(
    api_client: ApiClient,
    organizer_form_factory: OrganizerFormFactory,
    faker: Faker,
    gateway: Gateway,
) -> None:
    """Two different users cannot register as organizers with the same phone number."""
    # Arrange
    admin = await gateway.admin.create()
    with api_client.authenticate(auth_user_id=admin.auth_id):
        invite1 = (await api_client.issue_invite({})).assert_status(200).ensure_content()
        invite2 = (await api_client.issue_invite({})).assert_status(200).ensure_content()

    first_form = organizer_form_factory.build(invite_code=invite1.code)
    second_form = organizer_form_factory.build(invite_code=invite2.code).model_copy(
        update={"phone_number": first_form.phone_number},
    )

    # Act
    with api_client.authenticate(auth_user_id=str(uuid4()), auth_user_email=faker.email()):
        first_response = await api_client.register_organizer(first_form.model_dump(mode="json"))
    with api_client.authenticate(auth_user_id=str(uuid4()), auth_user_email=faker.email()):
        second_response = await api_client.register_organizer(second_form.model_dump(mode="json"))

    # Assert
    first_response.assert_status(200).ensure_content()
    second_response.assert_error(409, "ORGANIZER_ALREADY_EXISTS")


async def test_cannot_register_two_organizers_with_same_email_and_phone(
    api_client: ApiClient,
    organizer_form_factory: OrganizerFormFactory,
    faker: Faker,
    gateway: Gateway,
) -> None:
    """Two different users cannot register as organizers sharing both email and phone."""
    # Arrange
    admin = await gateway.admin.create()
    with api_client.authenticate(auth_user_id=admin.auth_id):
        invite1 = (await api_client.issue_invite({})).assert_status(200).ensure_content()
        invite2 = (await api_client.issue_invite({})).assert_status(200).ensure_content()

    shared_email = faker.email()
    first_form = organizer_form_factory.build(invite_code=invite1.code)
    second_form = organizer_form_factory.build(invite_code=invite2.code).model_copy(
        update={"phone_number": first_form.phone_number},
    )

    # Act
    with api_client.authenticate(auth_user_id=str(uuid4()), auth_user_email=shared_email):
        first_response = await api_client.register_organizer(first_form.model_dump(mode="json"))
    with api_client.authenticate(auth_user_id=str(uuid4()), auth_user_email=shared_email):
        second_response = await api_client.register_organizer(second_form.model_dump(mode="json"))

    # Assert
    first_response.assert_status(200).ensure_content()
    second_response.assert_error(409, "ORGANIZER_ALREADY_EXISTS")


async def test_register_with_nonexistent_invite_code_fails(
    api_client: ApiClient,
    organizer_form_factory: OrganizerFormFactory,
    faker: Faker,
) -> None:
    """Registering with a nonexistent invite code fails with INVITE_NOT_FOUND."""
    with api_client.authenticate(auth_user_id=str(uuid4()), auth_user_email=faker.email()):
        response = await api_client.register_organizer(
            organizer_form_factory.build(invite_code="nonexistent-code").model_dump(mode="json"),
        )

    response.assert_error(404, "INVITE_NOT_FOUND")


async def test_register_with_too_long_invite_code_fails_validation(
    api_client: ApiClient,
    organizer_form_factory: OrganizerFormFactory,
    faker: Faker,
) -> None:
    """Registering with an oversized invite code is rejected before invite lookup."""
    # Arrange
    data = organizer_form_factory.build().model_copy(
        update={"invite_code": "a" * (MAX_INVITE_CODE_LENGTH + 1)},
    )

    # Act
    with api_client.authenticate(auth_user_id=str(uuid4()), auth_user_email=faker.email()):
        response = await api_client.register_organizer(data.model_dump(mode="json"))

    # Assert
    response.assert_error(422, "VALIDATION_ERROR")


async def test_register_with_revoked_invite_code_fails(
    api_client: ApiClient,
    organizer_form_factory: OrganizerFormFactory,
    faker: Faker,
    gateway: Gateway,
) -> None:
    """Registering with a revoked invite code fails with INVITE_REVOKED."""
    # Arrange
    admin = await gateway.admin.create()
    with api_client.authenticate(auth_user_id=admin.auth_id):
        invite = (await api_client.issue_invite({})).assert_status(200).ensure_content()
        await api_client.revoke_invite(invite.invite_id)

    # Act
    with api_client.authenticate(auth_user_id=str(uuid4()), auth_user_email=faker.email()):
        response = await api_client.register_organizer(
            organizer_form_factory.build(invite_code=invite.code).model_dump(mode="json"),
        )

    response.assert_error(403, "INVITE_REVOKED")


async def test_register_with_used_invite_code_fails(
    api_client: ApiClient,
    organizer_form_factory: OrganizerFormFactory,
    faker: Faker,
    gateway: Gateway,
) -> None:
    """Registering with an already-used invite code fails with INVITE_ALREADY_USED."""
    # Arrange
    admin = await gateway.admin.create()
    with api_client.authenticate(auth_user_id=admin.auth_id):
        invite = (await api_client.issue_invite({})).assert_status(200).ensure_content()

    # Act
    with api_client.authenticate(auth_user_id=str(uuid4()), auth_user_email=faker.email()):
        await api_client.register_organizer(
            organizer_form_factory.build(invite_code=invite.code).model_dump(mode="json"),
        )

    with api_client.authenticate(auth_user_id=str(uuid4()), auth_user_email=faker.email()):
        response = await api_client.register_organizer(
            organizer_form_factory.build(invite_code=invite.code).model_dump(mode="json"),
        )

    response.assert_error(409, "INVITE_ALREADY_USED")


async def test_concurrent_registrations_with_same_invite_use_invite_once(
    api_client: ApiClient,
    organizer_form_factory: OrganizerFormFactory,
    faker: Faker,
    gateway: Gateway,
) -> None:
    """Concurrent registrations with one invite use it exactly once."""
    # Arrange
    admin = await gateway.admin.create()
    with api_client.authenticate(auth_user_id=admin.auth_id):
        invite = (await api_client.issue_invite({})).assert_status(200).ensure_content()

    first_form = organizer_form_factory.build(invite_code=invite.code)
    second_form = organizer_form_factory.build(invite_code=invite.code)

    async def register(data: dict[str, Any]) -> APIResponse[CreatedOrganizer]:
        with api_client.authenticate(auth_user_id=str(uuid4()), auth_user_email=faker.email()):
            return await api_client.register_organizer(data)

    # Act
    responses = await asyncio.gather(
        register(first_form.model_dump(mode="json")),
        register(second_form.model_dump(mode="json")),
    )
    with api_client.authenticate(auth_user_id=admin.auth_id):
        actual = (await api_client.read_invite(invite.invite_id)).assert_status(200).ensure_content()

    # Assert
    statuses = [response.status for response in responses]
    assert sorted(statuses) == [200, 409]
    next(response for response in responses if response.status == 409).assert_error(409, "INVITE_ALREADY_USED")
    assert actual.is_used is True
    assert actual.is_revoked is False
    assert actual.used_by is not None


async def test_concurrent_register_and_revoke_invite_resolve_once(
    api_client: ApiClient,
    organizer_form_factory: OrganizerFormFactory,
    faker: Faker,
    gateway: Gateway,
) -> None:
    """Concurrent registration and revoke of one invite resolve it exactly once."""
    # Arrange
    admin = await gateway.admin.create()
    with api_client.authenticate(auth_user_id=admin.auth_id):
        invite = (await api_client.issue_invite({})).assert_status(200).ensure_content()

    form = organizer_form_factory.build(invite_code=invite.code)

    async def register() -> APIResponse[CreatedOrganizer]:
        with api_client.authenticate(auth_user_id=str(uuid4()), auth_user_email=faker.email()):
            return await api_client.register_organizer(form.model_dump(mode="json"))

    async def revoke() -> APIResponse[None]:
        with api_client.authenticate(auth_user_id=admin.auth_id):
            return await api_client.revoke_invite(invite.invite_id)

    # Act
    register_response, revoke_response = await asyncio.gather(register(), revoke())
    with api_client.authenticate(auth_user_id=admin.auth_id):
        actual = (await api_client.read_invite(invite.invite_id)).assert_status(200).ensure_content()

    # Assert
    register_status = register_response.status
    revoke_status = revoke_response.status
    assert register_status == 200 or revoke_status == 200
    assert not (register_status == 200 and revoke_status == 200)
    if register_status == 200:
        revoke_response.assert_error(409, "INVITE_ALREADY_USED")
        assert actual.is_used is True
        assert actual.is_revoked is False
        assert actual.used_by is not None
    else:
        register_response.assert_error(403, "INVITE_REVOKED")
        assert actual.is_revoked is True
        assert actual.is_used is False


async def test_concurrent_organizer_registrations_with_same_email_create_one_organizer(
    api_client: ApiClient,
    organizer_form_factory: OrganizerFormFactory,
    faker: Faker,
    gateway: Gateway,
) -> None:
    """Concurrent organizer registrations with the same contact email create exactly one organizer."""
    # Arrange
    admin = await gateway.admin.create()
    with api_client.authenticate(auth_user_id=admin.auth_id):
        first_invite = (await api_client.issue_invite({})).assert_status(200).ensure_content()
        second_invite = (await api_client.issue_invite({})).assert_status(200).ensure_content()

    shared_email = faker.email()
    first_form = organizer_form_factory.build(invite_code=first_invite.code)
    second_form = organizer_form_factory.build(invite_code=second_invite.code)

    async def register(data: dict[str, Any]) -> APIResponse[CreatedOrganizer]:
        with api_client.authenticate(auth_user_id=str(uuid4()), auth_user_email=shared_email):
            return await api_client.register_organizer(data)

    # Act
    responses = await asyncio.gather(
        register(first_form.model_dump(mode="json")),
        register(second_form.model_dump(mode="json")),
    )

    # Assert
    assert_one_success_one_error(responses, _ORGANIZER_UNIQUENESS_RACE_ERRORS)


async def test_concurrent_organizer_registrations_with_same_phone_create_one_organizer(
    api_client: ApiClient,
    organizer_form_factory: OrganizerFormFactory,
    faker: Faker,
    gateway: Gateway,
) -> None:
    """Concurrent organizer registrations with the same phone create exactly one organizer."""
    # Arrange
    admin = await gateway.admin.create()
    with api_client.authenticate(auth_user_id=admin.auth_id):
        first_invite = (await api_client.issue_invite({})).assert_status(200).ensure_content()
        second_invite = (await api_client.issue_invite({})).assert_status(200).ensure_content()

    first_form = organizer_form_factory.build(invite_code=first_invite.code)
    second_form = organizer_form_factory.build(invite_code=second_invite.code).model_copy(
        update={"phone_number": first_form.phone_number},
    )

    async def register(data: dict[str, Any]) -> APIResponse[CreatedOrganizer]:
        with api_client.authenticate(auth_user_id=str(uuid4()), auth_user_email=faker.email()):
            return await api_client.register_organizer(data)

    # Act
    responses = await asyncio.gather(
        register(first_form.model_dump(mode="json")),
        register(second_form.model_dump(mode="json")),
    )

    # Assert
    assert_one_success_one_error(responses, _ORGANIZER_UNIQUENESS_RACE_ERRORS)
