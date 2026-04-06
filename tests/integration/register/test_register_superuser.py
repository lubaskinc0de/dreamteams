from dreamteams.application.register.register_organizer import CreatedOrganizer
from dreamteams.application.register.register_participant import CreatedParticipant
from dreamteams.application.register.register_superuser import CreatedSuperuser
from tests.integration.api_client import ApiClient
from tests.integration.constants import SUPERUSER_ID, SUPERUSER_PASSWORD, USER_ID


async def test_register_superuser(api_client: ApiClient) -> None:
    """Registering with the correct password creates a new superuser."""
    with api_client.authenticate(auth_user_id=SUPERUSER_ID):
        response = await api_client.register_superuser({"password": SUPERUSER_PASSWORD})

    result = response.assert_status(200).ensure_content()
    assert isinstance(result, CreatedSuperuser)


async def test_register_superuser_wrong_password(api_client: ApiClient) -> None:
    """Registering with an incorrect password fails with INVALID_SUPERUSER_PASSWORD."""
    with api_client.authenticate(auth_user_id=SUPERUSER_ID):
        response = await api_client.register_superuser({"password": "wrongpassword"})

    response.assert_error(403, "INVALID_SUPERUSER_PASSWORD")


async def test_register_superuser_twice_is_idempotent(api_client: ApiClient) -> None:
    """Registering as superuser twice succeeds and returns the same user ID."""
    with api_client.authenticate(auth_user_id=SUPERUSER_ID):
        first = await api_client.register_superuser({"password": SUPERUSER_PASSWORD})
        second = await api_client.register_superuser({"password": SUPERUSER_PASSWORD})

    first_result = first.assert_status(200).ensure_content()
    second_result = second.assert_status(200).ensure_content()
    assert first_result.user_id == second_result.user_id


async def test_register_superuser_unauthenticated(api_client: ApiClient) -> None:
    """Registering a superuser without authentication fails with UNAUTHORIZED."""
    response = await api_client.register_superuser({"password": SUPERUSER_PASSWORD})

    response.assert_error(401, "UNAUTHORIZED")


async def test_register_superuser_as_existing_organizer(
    api_client: ApiClient,
    organizer: CreatedOrganizer,
) -> None:
    """An existing organizer can register as superuser, gaining admin rights on the same user."""
    with api_client.authenticate(auth_user_id=USER_ID):
        response = await api_client.register_superuser({"password": SUPERUSER_PASSWORD})

    result = response.assert_status(200).ensure_content()

    assert result.user_id == organizer.user_id


async def test_register_superuser_as_existing_participant(
    api_client: ApiClient,
    participant: CreatedParticipant,
) -> None:
    """An existing participant can register as superuser, gaining admin rights on the same user."""
    with api_client.authenticate(auth_user_id=USER_ID):
        response = await api_client.register_superuser({"password": SUPERUSER_PASSWORD})

    result = response.assert_status(200).ensure_content()

    assert result.user_id == participant.user_id
