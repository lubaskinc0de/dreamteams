from contextvars import ContextVar, Token
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Self

from adaptix import Retort
from adaptix.load_error import LoadError
from aiohttp import ClientResponse, ClientResponseError, ClientSession, FormData

from dreamteams.adapters.auth.model import AuthUserId
from dreamteams.adapters.errors.http.response import ErrorResponse
from dreamteams.application.common.gateway.application import ApplicationSortBy
from dreamteams.application.common.gateway.competition import CompetitionSortBy, ExploreSortBy
from dreamteams.application.common.gateway.sorting import SortOrder
from dreamteams.application.explore_competitions import CreatedApplication, ExploreCompetitionsList
from dreamteams.application.manage_application_form import ApplicationFormModel, CreatedApplicationForm
from dreamteams.application.manage_applications import ApplicationsList
from dreamteams.application.manage_competitions import CompetitionModel, CompetitionsList
from dreamteams.application.manage_invites import InviteIssued, InviteModel, InvitesList
from dreamteams.application.manage_my_applications import ApplicationModel
from dreamteams.application.manage_my_applications import ApplicationsList as MyApplicationsList
from dreamteams.application.manage_profile import ProfileModel
from dreamteams.application.preview_competition.list import PreviewCompetitionsList
from dreamteams.application.publish_competition import CreatedCompetition
from dreamteams.application.register.register_organizer import CreatedOrganizer
from dreamteams.application.register.register_participant import CreatedParticipant
from dreamteams.application.register.register_superuser import CreatedSuperuser
from dreamteams.entities.application.entity import ApplicationStatus
from dreamteams.entities.common.identifiers import ApplicationId, CompetitionId, OrganizerInviteId
from dreamteams.entities.common.vo.domain import Domain

retort = Retort()

ORGANIZER_URL = "/organizers"
USERS_URL = "/users"
SUPERUSER_URL = f"{USERS_URL}/superuser/"
COMPETITIONS_URL = "/competitions"
INVITES_URL = "/invites"
PARTICIPANT_URL = "/participants"
APPLICATIONS_URL = "/applications"


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
    """Context manager for setting authentication.

    Auth headers live in a ``ContextVar`` so concurrent tasks (e.g. ``asyncio.gather``)
    each carry their own snapshot and do not overwrite each other's credentials.
    """

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
        self._token: Token[dict[str, str] | None] | None = None

    def __enter__(self) -> None:
        """Set authentication headers for the duration of the context."""
        headers = {self._config.auth_user_id_header: self._auth_user_id}
        if self._access_token:
            headers[self._config.access_token_header] = self._access_token
        if self._auth_user_email is not None:
            headers[self._config.auth_user_email_header] = self._auth_user_email
        self._token = self._api_client._push_auth(headers)  # noqa: SLF001

    def __exit__(self, *exc_info: object) -> None:
        """Reset authentication headers after the context."""
        assert self._token is not None
        self._api_client._pop_auth(self._token)  # noqa: SLF001
        if exc_info[0] is not None:  # exc type
            raise exc_info[1]  # type: ignore[misc] # exc value


class ApiClient:
    """Client for making API requests."""

    def __init__(
        self,
        session: ClientSession,
        config: APIClientConfig,
        access_token: str | None,
    ) -> None:
        self.session = session
        self._auth_headers: ContextVar[dict[str, str] | None] = ContextVar("_auth_headers", default=None)
        self._config = config
        self._access_token = access_token

    @property
    def _headers(self) -> dict[str, str]:
        """Current auth headers for the calling task."""
        return self._auth_headers.get() or {}

    def _push_auth(self, headers: dict[str, str]) -> Token[dict[str, str] | None]:
        """Install auth headers for the calling task; call ``_pop_auth`` to restore."""
        return self._auth_headers.set(headers)

    def _pop_auth(self, token: Token[dict[str, str] | None]) -> None:
        """Restore prior auth headers using the token returned by ``_push_auth``."""
        self._auth_headers.reset(token)

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

    async def register_participant(self, data: dict[str, Any]) -> APIResponse[CreatedParticipant]:
        """Register as participant via POST /participants/."""
        url = PARTICIPANT_URL
        async with self.session.post(url, headers=self._headers, json=data) as response:
            return await self._load_response(
                response,
                response_type=CreatedParticipant,
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

    async def explore_competitions(
        self,
        *,
        page: int = 1,
        sort_by: ExploreSortBy = ExploreSortBy.MOST_POPULAR,
        search: str | None = None,
        min_team_size: int | None = None,
        max_team_size: int | None = None,
        auto_accept: bool | None = None,
        domains: list[Domain] | None = None,
    ) -> APIResponse[ExploreCompetitionsList]:
        """Call GET /competitions/explore (participant-facing)."""
        params: list[tuple[str, str | int]] = [
            ("page", page),
            ("sort_by", sort_by.value),
        ]
        if search is not None:
            params.append(("search", search))
        if min_team_size is not None:
            params.append(("min_team_size", min_team_size))
        if max_team_size is not None:
            params.append(("max_team_size", max_team_size))
        if auto_accept is not None:
            params.append(("auto_accept", str(auto_accept).lower()))
        if domains is not None:
            params.extend(("domains", domain.value) for domain in domains)

        async with self.session.get(
            f"{COMPETITIONS_URL}/explore",
            headers=self._headers,
            params=params,
        ) as response:
            return await self._load_response(response, response_type=ExploreCompetitionsList)

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

    async def create_application_form(
        self,
        competition_id: CompetitionId,
        data: dict[str, Any],
    ) -> APIResponse[CreatedApplicationForm]:
        """Create application form via POST /competitions/{competition_id}/application-form/."""
        url = f"{COMPETITIONS_URL}/{competition_id}/application-form/"
        async with self.session.post(url, headers=self._headers, json=data) as response:
            return await self._load_response(response, response_type=CreatedApplicationForm)

    async def read_application_form(self, competition_id: CompetitionId) -> APIResponse[ApplicationFormModel]:
        """Read application form via GET /competitions/{competition_id}/application-form/."""
        url = f"{COMPETITIONS_URL}/{competition_id}/application-form/"
        async with self.session.get(url, headers=self._headers) as response:
            return await self._load_response(response, response_type=ApplicationFormModel)

    async def delete_application_form(self, competition_id: CompetitionId) -> APIResponse[None]:
        """Delete application form via DELETE /competitions/{competition_id}/application-form/."""
        url = f"{COMPETITIONS_URL}/{competition_id}/application-form/"
        async with self.session.delete(url, headers=self._headers) as response:
            return await self._load_response(response, response_type=None)

    async def submit_application(
        self,
        competition_id: CompetitionId,
        data: dict[str, Any],
    ) -> APIResponse[CreatedApplication]:
        """Submit an application via POST /competitions/{competition_id}/applications/."""
        url = f"{COMPETITIONS_URL}/{competition_id}/applications/"
        async with self.session.post(url, headers=self._headers, json=data) as response:
            return await self._load_response(response, response_type=CreatedApplication)

    async def list_applications_by_competition(
        self,
        competition_id: CompetitionId,
        page: int = 1,
        *,
        sort_by: ApplicationSortBy = ApplicationSortBy.CREATED_AT,
        sort_order: SortOrder = SortOrder.DESC,
        status: ApplicationStatus | None = None,
    ) -> APIResponse[ApplicationsList]:
        """List applications for a competition via GET /competitions/{competition_id}/applications/."""
        url = f"{COMPETITIONS_URL}/{competition_id}/applications/"
        params: dict[str, str | int] = {
            "page": page,
            "sort_by": sort_by.value,
            "sort_order": sort_order.value,
        }
        if status is not None:
            params["status"] = status.value
        async with self.session.get(url, headers=self._headers, params=params) as response:
            return await self._load_response(response, response_type=ApplicationsList)

    async def list_my_applications(
        self,
        page: int = 1,
        *,
        sort_by: ApplicationSortBy = ApplicationSortBy.CREATED_AT,
        sort_order: SortOrder = SortOrder.DESC,
        status: ApplicationStatus | None = None,
    ) -> APIResponse[MyApplicationsList]:
        """List own applications via GET /applications/."""
        params: dict[str, str | int] = {
            "page": page,
            "sort_by": sort_by.value,
            "sort_order": sort_order.value,
        }
        if status is not None:
            params["status"] = status.value
        async with self.session.get(APPLICATIONS_URL + "/", headers=self._headers, params=params) as response:
            return await self._load_response(response, response_type=MyApplicationsList)

    async def read_my_application(self, application_id: ApplicationId) -> APIResponse[ApplicationModel]:
        """Read own application via GET /applications/{application_id}/my/."""
        url = f"{APPLICATIONS_URL}/{application_id}/my/"
        async with self.session.get(url, headers=self._headers) as response:
            return await self._load_response(response, response_type=ApplicationModel)

    async def read_application(self, application_id: ApplicationId) -> APIResponse[ApplicationModel]:
        """Read application (organizer) via GET /applications/{application_id}/."""
        url = f"{APPLICATIONS_URL}/{application_id}/"
        async with self.session.get(url, headers=self._headers) as response:
            return await self._load_response(response, response_type=ApplicationModel)

    async def withdraw_application(self, application_id: ApplicationId) -> APIResponse[None]:
        """Withdraw application via DELETE /applications/{application_id}/."""
        url = f"{APPLICATIONS_URL}/{application_id}/"
        async with self.session.delete(url, headers=self._headers) as response:
            return await self._load_response(response, response_type=None)

    async def accept_application(self, application_id: ApplicationId) -> APIResponse[None]:
        """Accept application via POST /applications/{application_id}/accept/."""
        url = f"{APPLICATIONS_URL}/{application_id}/accept/"
        async with self.session.post(url, headers=self._headers) as response:
            return await self._load_response(response, response_type=None)

    async def reject_application(self, application_id: ApplicationId) -> APIResponse[None]:
        """Reject application via POST /applications/{application_id}/reject/."""
        url = f"{APPLICATIONS_URL}/{application_id}/reject/"
        async with self.session.post(url, headers=self._headers) as response:
            return await self._load_response(response, response_type=None)

    async def update_participant(self, data: dict[str, Any]) -> APIResponse[None]:
        """Update participant profile via PUT /users/me/participant."""
        url = f"{USERS_URL}/me/participant"
        async with self.session.put(url, headers=self._headers, json=data) as response:
            return await self._load_response(response, response_type=None)

    async def update_organizer(self, data: dict[str, Any]) -> APIResponse[None]:
        """Update organizer profile via PUT /users/me/organizer."""
        url = f"{USERS_URL}/me/organizer"
        async with self.session.put(url, headers=self._headers, json=data) as response:
            return await self._load_response(response, response_type=None)
