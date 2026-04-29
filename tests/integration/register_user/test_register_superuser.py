from uuid import uuid4

from dreamteams.application.register_user.register_superuser import CreatedSuperuser
from tests.integration.api_client import ApiClient
from tests.integration.helpers.facade import Gateway

_SUPERUSER_PASSWORD = "asd123321"


async def test_register_superuser(api_client: ApiClient) -> None:
    """Registering with the correct password creates a new superuser."""
    # Arrange
    auth_id = str(uuid4())

    # Act
    with api_client.authenticate(auth_user_id=auth_id):
        response = await api_client.register_superuser({"password": _SUPERUSER_PASSWORD})

    # Assert
    result = response.assert_status(200).ensure_content()
    assert isinstance(result, CreatedSuperuser)


async def test_register_superuser_wrong_password(api_client: ApiClient) -> None:
    """Registering with an incorrect password fails with INVALID_SUPERUSER_PASSWORD."""
    # Arrange
    auth_id = str(uuid4())

    # Act
    with api_client.authenticate(auth_user_id=auth_id):
        response = await api_client.register_superuser({"password": "wrongpassword"})

    # Assert
    response.assert_error(403, "INVALID_SUPERUSER_PASSWORD")


async def test_register_superuser_twice_is_idempotent(api_client: ApiClient) -> None:
    """Registering as superuser twice succeeds and returns the same user ID."""
    # Arrange
    auth_id = str(uuid4())

    # Act
    with api_client.authenticate(auth_user_id=auth_id):
        first = await api_client.register_superuser({"password": _SUPERUSER_PASSWORD})
        second = await api_client.register_superuser({"password": _SUPERUSER_PASSWORD})

    # Assert
    first_result = first.assert_status(200).ensure_content()
    second_result = second.assert_status(200).ensure_content()
    assert first_result.user_id == second_result.user_id


async def test_register_superuser_unauthenticated(api_client: ApiClient) -> None:
    """Registering a superuser without authentication fails with UNAUTHORIZED."""
    # Act
    response = await api_client.register_superuser({"password": _SUPERUSER_PASSWORD})

    # Assert
    response.assert_error(401, "UNAUTHORIZED")


async def test_register_superuser_as_existing_organizer(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """An existing organizer can register as superuser, gaining admin rights on the same user."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)

    # Act
    with api_client.authenticate(auth_user_id=owner.organizer.auth_id):
        response = await api_client.register_superuser({"password": _SUPERUSER_PASSWORD})

    # Assert
    result = response.assert_status(200).ensure_content()
    assert result.user_id == owner.organizer.created.user_id


async def test_register_superuser_as_existing_participant(
    api_client: ApiClient,
    gateway: Gateway,
) -> None:
    """An existing participant can register as superuser, gaining admin rights on the same user."""
    # Arrange
    participant = await gateway.participant.create()

    # Act
    with api_client.authenticate(auth_user_id=participant.auth_id):
        response = await api_client.register_superuser({"password": _SUPERUSER_PASSWORD})

    # Assert
    result = response.assert_status(200).ensure_content()
    assert result.user_id == participant.created.user_id
