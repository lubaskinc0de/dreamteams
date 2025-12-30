from dataclasses import dataclass
from typing import Any, Self

from adaptix import Retort
from adaptix.load_error import LoadError
from aiohttp import ClientResponse, ClientResponseError, ClientSession

from dreamteams.adapters.auth.model import AuthUserId
from dreamteams.adapters.errors.http.response import ErrorResponse
from dreamteams.adapters.tracing import TraceId, TracingConfig
from dreamteams.application.create_competition.interactor import CreatedCompetition
from dreamteams.application.register.organizer import CreatedOrganizer
from dreamteams.application.view_profile.interactor import ProfileModel

retort = Retort()

ORGANIZER_URL = "/organizers"
USERS_URL = "/users"
COMPETITIONS_URL = "/competitions"


@dataclass
class EmptyResponse:
    """Empty response."""


@dataclass(slots=True, frozen=True)
class APIResponse[T]:
    """Response from API."""

    content: T | None
    http_response: ClientResponse
    status: int
    error: ErrorResponse | None = None

    def ensure_err(self) -> ErrorResponse:
        """Unwrap error response or raise ValueError if there is no error."""
        if self.error is None:
            msg = f"Cannot unwrap error, content = {self.content}"
            raise ValueError(msg)
        return self.error

    def ensure_ok(self) -> T:
        """Unwrap successful response or raise ValueError if error occurred."""
        if self.content is None:
            msg = f"Cannot unwrap response, status = {self.status}, error = {self.error}"
            raise ValueError(msg)
        return self.content

    def assert_status(self, status: int) -> Self:
        """Assert that response status matches expected value."""
        if self.status != status:
            msg = f"HTTP status assertion failed. {self.status} != {status}"
            raise ValueError(msg)
        return self

    def assert_error(self, status: int, error_code: str) -> Self:
        """Assert that response status matches expected value, response is ``ErrorResponse`` and error code matches."""
        if self.status != status:
            msg = f"HTTP status assertion failed. {self.status} != {status}"
            raise ValueError(msg)

        if self.ensure_err().code != error_code:
            msg = "Error code does not equal"
            raise ValueError(msg)

        return self


@dataclass(slots=True, frozen=True, kw_only=True)
class APIClientConfig:
    """Config for APIClient."""

    auth_user_id_header: str
    auth_user_email_header: str
    access_token_header: str


class AuthContext:
    """Context manager for setting authentication."""

    def __init__(
        self,
        api_client: "ApiClient",
        auth_user_id: AuthUserId,
        auth_user_email: str | None,
        config: APIClientConfig,
        access_token: str | None,
    ) -> None:
        self._api_client = api_client
        self._auth_user_id = auth_user_id
        self._auth_user_email = auth_user_email
        self._config = config
        self._access_token = access_token

    def __enter__(self) -> None:
        """Set authentication header for the duration of the context."""
        self._api_client.set_header(self._config.auth_user_id_header, self._auth_user_id)
        if self._access_token:
            self._api_client.set_header(
                self._config.access_token_header,
                self._access_token,
            )
        if self._auth_user_email is not None:
            self._api_client.set_header(
                self._config.auth_user_email_header,
                self._auth_user_email,
            )

    def __exit__(self, *exc_info: object) -> None:
        """Remove authentication header after the context."""
        self._api_client.remove_header(self._config.auth_user_id_header)
        if exc_info[0] is not None:  # exc type
            raise exc_info[1]  # type: ignore[misc] # exc value


class ApiClient:
    """Client for making API requests."""

    def __init__(
        self,
        session: ClientSession,
        config: APIClientConfig,
        trace_id: TraceId,
        tracing_config: TracingConfig,
        access_token: str | None,
    ) -> None:
        self.session = session
        self.trace_id = trace_id
        self._headers: dict[str, str] = {
            tracing_config.trace_id_header: self.trace_id,
        }
        self._config = config
        self._access_token = access_token

    async def _load_response[T](self, response: ClientResponse, response_type: type[T] | None) -> APIResponse[T]:
        """Load response content or error from HTTP response."""
        try:
            response.raise_for_status()
        except ClientResponseError as response_error:
            try:
                return APIResponse(
                    content=None,
                    error=retort.load(await response.json(), ErrorResponse),
                    status=response.status,
                    http_response=response,
                )
            except LoadError as load_error:
                raise load_error from response_error
        else:
            return APIResponse(
                content=retort.load(await response.json(), response_type),
                http_response=response,
                status=response.status,
            )

    def set_header(self, header: str, value: str) -> None:
        """Add HTTP header."""
        self._headers[header] = value

    def remove_header(self, header: str) -> None:
        """Remove HTTP header."""
        del self._headers[header]

    def authenticate(self, *, auth_user_id: AuthUserId, auth_user_email: str | None = None) -> AuthContext:
        """Set auth user ID for requests."""
        return AuthContext(self, auth_user_id, auth_user_email, self._config, self._access_token)

    async def readiness(self) -> APIResponse[EmptyResponse]:
        """GET /internal/ready."""
        url = "/internal/ready"
        async with self.session.get(url, headers=self._headers) as response:
            return await self._load_response(
                response,
                response_type=EmptyResponse,
            )

    async def liveness(self) -> APIResponse[EmptyResponse]:
        """GET /internal/alive."""
        url = "/internal/alive"
        async with self.session.get(url, headers=self._headers) as response:
            return await self._load_response(
                response,
                response_type=EmptyResponse,
            )

    async def register_organizer(self, data: dict[str, Any]) -> APIResponse[CreatedOrganizer]:
        """Register as organizer via POST /organizers/."""
        url = ORGANIZER_URL
        async with self.session.post(url, headers=self._headers, json=data) as response:
            return await self._load_response(
                response,
                response_type=CreatedOrganizer,
            )

    async def view_profile(self) -> APIResponse[ProfileModel]:
        """View user profile via GET /users/me."""
        url = f"{USERS_URL}/me"
        async with self.session.get(url, headers=self._headers) as response:
            return await self._load_response(
                response,
                response_type=ProfileModel,
            )

    async def create_competition(self, data: dict[str, Any]) -> APIResponse[CreatedCompetition]:
        """Create competition via POST /competitions/."""
        url = COMPETITIONS_URL
        async with self.session.post(url, headers=self._headers, json=data) as response:
            return await self._load_response(
                response,
                response_type=CreatedCompetition,
            )
