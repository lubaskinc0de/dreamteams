from dataclasses import dataclass
from pathlib import Path
from typing import Any, Self

from adaptix import Retort
from adaptix.load_error import LoadError
from aiohttp import ClientResponse, ClientResponseError, ClientSession, FormData

from dreamteams.adapters.auth.model import AuthUserId
from dreamteams.adapters.errors.http.response import ErrorResponse
from dreamteams.adapters.tracing import TraceId, TracingConfig
from dreamteams.application.common.gateway.competition import CompetitionSortBy
from dreamteams.application.common.gateway.sorting import SortOrder
from dreamteams.application.manage_competitions import CompetitionModel, CompetitionsList
from dreamteams.application.manage_invites import InviteIssued, InviteModel, InvitesList
from dreamteams.application.manage_profile import ProfileModel
from dreamteams.application.preview_competition.list import PreviewCompetitionsList
from dreamteams.application.publish_competition import CreatedCompetition
from dreamteams.application.register.register_organizer import CreatedOrganizer
from dreamteams.application.register.register_superuser import CreatedSuperuser
from dreamteams.entities.common.identifiers import CompetitionId, OrganizerInviteId

retort = Retort()

ORGANIZER_URL = "/organizers"
USERS_URL = "/users"
SUPERUSER_URL = f"{USERS_URL}/superuser/"
COMPETITIONS_URL = "/competitions"
INVITES_URL = "/invites"


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

    def ensure_content(self) -> T:
        """Unwrap successful response or raise ValueError if error occurred."""
        if self.content is None:
            msg = f"Cannot unwrap response, status = {self.status}, error = {self.error}"
            raise ValueError(msg)
        return self.content

    def assert_status(self, status: int) -> Self:
        """Assert that response status matches expected value."""
        if self.status != status:
            msg = f"HTTP status assertion failed. {self.status} != {status}."
            raise ValueError(msg)
        return self

    def assert_error(self, status: int, error_code: str) -> Self:
        """Assert that response status matches expected value, response is ``ErrorResponse`` and error code matches."""
        self.assert_status(status)
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

    @property
    def headers(self) -> dict[str, str]:
        """API client headers."""
        return self._headers

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

    async def register_superuser(self, data: dict[str, Any]) -> APIResponse[CreatedSuperuser]:
        """Register as superuser via POST /users/superuser/."""
        async with self.session.post(SUPERUSER_URL, headers=self._headers, json=data) as response:
            return await self._load_response(response, response_type=CreatedSuperuser)

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

    async def delete_profile(self) -> APIResponse[None]:
        """Delete user profile via DELETE /users/me."""
        url = f"{USERS_URL}/me"
        async with self.session.delete(url, headers=self._headers) as response:
            return await self._load_response(
                response,
                response_type=None,
            )

    async def detach_avatar(self) -> APIResponse[None]:
        """Detach user avatar via DELETE /users/me/avatar."""
        url = f"{USERS_URL}/me/avatar"
        async with self.session.delete(url, headers=self._headers) as response:
            return await self._load_response(
                response,
                response_type=None,
            )

    async def attach_avatar(
        self,
        image_path: Path,
        filename: str = "image.jpg",
        content_type: str = "image/jpeg",
    ) -> APIResponse[None]:
        """Attach user avatar via PUT /users/me/avatar."""
        with image_path.open("rb") as f:
            url = f"{USERS_URL}/me/avatar"
            data = FormData()
            data.add_field(
                name="file",
                value=f,
                filename=filename,
                content_type=content_type,
            )
            async with self.session.put(url, headers=self._headers, data=data) as response:
                return await self._load_response(
                    response,
                    response_type=None,
                )

    async def create_competition(self, data: dict[str, Any]) -> APIResponse[CreatedCompetition]:
        """Create competition via POST /competitions/."""
        url = COMPETITIONS_URL
        async with self.session.post(url, headers=self._headers, json=data) as response:
            return await self._load_response(
                response,
                response_type=CreatedCompetition,
            )

    async def list_competitions(
        self,
        *,
        page: int = 1,
        sort_by: CompetitionSortBy | None = None,
        sort_order: SortOrder | None = None,
        is_archived: bool | None = None,
        search: str | None = None,
    ) -> APIResponse[CompetitionsList]:
        """List competitions via GET /competitions/."""
        params = {
            "page": page,
            "sort_by": sort_by,
            "sort_order": sort_order,
            "is_archived": int(is_archived) if is_archived is not None else None,
            "search": search,
        }
        url = f"{COMPETITIONS_URL}"
        async with self.session.get(
            url,
            headers=self._headers,
            params={name: value for name, value in params.items() if value is not None},
        ) as response:
            return await self._load_response(
                response,
                response_type=CompetitionsList,
            )

    async def list_preview_competitions(self, page: int = 1) -> APIResponse[PreviewCompetitionsList]:
        """Call GET /preview/competitions endpoint."""
        params = {
            "page": page,
        }

        async with self.session.get(f"{COMPETITIONS_URL}/preview/", headers=self._headers, params=params) as response:
            return await self._load_response(response, response_type=PreviewCompetitionsList)

    async def read_competition(self, competition_id: CompetitionId) -> APIResponse[CompetitionModel]:
        """Read competition via GET /competitions/{competition_id}."""
        url = f"{COMPETITIONS_URL}/{competition_id}"
        async with self.session.get(url, headers=self._headers) as response:
            return await self._load_response(
                response,
                response_type=CompetitionModel,
            )

    async def update_competition(
        self,
        competition_id: CompetitionId,
        data: dict[str, Any],
    ) -> APIResponse[None]:
        """Update competition via PUT /competitions/{competition_id}."""
        url = f"{COMPETITIONS_URL}/{competition_id}"
        async with self.session.put(url, headers=self._headers, json=data) as response:
            return await self._load_response(
                response,
                response_type=None,
            )

    async def delete_competition(self, competition_id: CompetitionId) -> APIResponse[None]:
        """Delete competition via DELETE /competitions/{competition_id}."""
        url = f"{COMPETITIONS_URL}/{competition_id}"
        async with self.session.delete(url, headers=self._headers) as response:
            return await self._load_response(
                response,
                response_type=None,
            )

    async def issue_invite(self, data: dict[str, Any]) -> APIResponse[InviteIssued]:
        """Issue an organizer invite via POST /invites/."""
        async with self.session.post(INVITES_URL, headers=self._headers, json=data) as response:
            return await self._load_response(response, response_type=InviteIssued)

    async def list_invites(self, page: int = 1) -> APIResponse[InvitesList]:
        """List organizer invites via GET /invites/."""
        async with self.session.get(INVITES_URL, headers=self._headers, params={"page": page}) as response:
            return await self._load_response(response, response_type=InvitesList)

    async def read_invite(self, invite_id: OrganizerInviteId) -> APIResponse[InviteModel]:
        """Read a single organizer invite via GET /invites/{invite_id}."""
        url = f"{INVITES_URL}/{invite_id}"
        async with self.session.get(url, headers=self._headers) as response:
            return await self._load_response(response, response_type=InviteModel)

    async def revoke_invite(self, invite_id: OrganizerInviteId) -> APIResponse[None]:
        """Revoke an organizer invite via DELETE /invites/{invite_id}."""
        url = f"{INVITES_URL}/{invite_id}"
        async with self.session.delete(url, headers=self._headers) as response:
            return await self._load_response(response, response_type=None)
