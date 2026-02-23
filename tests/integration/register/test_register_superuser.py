from dreamteams.application.register.register_superuser import CreatedSuperuser
from tests.integration.api_client import ApiClient
from tests.integration.constants import SUPERUSER_ID, SUPERUSER_PASSWORD


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


async def test_register_superuser_twice_fails(api_client: ApiClient) -> None:
    """Registering a superuser with an already-registered auth user fails."""
    with api_client.authenticate(auth_user_id=SUPERUSER_ID):
        first = await api_client.register_superuser({"password": SUPERUSER_PASSWORD})
        second = await api_client.register_superuser({"password": SUPERUSER_PASSWORD})

    first.assert_status(200)
    second.assert_error(409, "AUTH_USER_ALREADY_EXISTS")


async def test_register_superuser_unauthenticated(api_client: ApiClient) -> None:
    """Registering a superuser without authentication fails with UNAUTHORIZED."""
    response = await api_client.register_superuser({"password": SUPERUSER_PASSWORD})

    response.assert_error(401, "UNAUTHORIZED")
