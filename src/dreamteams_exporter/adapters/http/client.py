import asyncio
from dataclasses import dataclass
from typing import Any
from uuid import UUID

import aiohttp
from adaptix import ExtraSkip, P, Retort, loader, name_mapping

from dreamteams_exporter.adapters.auth.model import AuthUserId
from dreamteams_exporter.adapters.http.config import DreamteamsApiConfig
from dreamteams_exporter.application.common.dto.application import ApplicationsPage
from dreamteams_exporter.application.errors.auth import UnauthorizedError
from dreamteams_exporter.entities.application.entity import Application
from dreamteams_exporter.entities.application_form.entity import ApplicationForm, ApplicationFormField
from dreamteams_exporter.entities.common.identifiers import CompetitionId
from dreamteams_exporter.entities.common.vo.application_status import ApplicationStatus
from dreamteams_exporter.entities.participant.entity import Participant
from dreamteams_exporter.entities.user import User

_HTTP_NOT_FOUND = 404
_HTTP_UNAUTHORIZED = frozenset({401, 403})
_RETRYABLE_HTTP_STATUSES = frozenset({502, 503, 504})


@dataclass(slots=True, frozen=True, kw_only=True)
class DreamTeamsApiResponse[T]:
    """Parsed response from the main DreamTeams API."""

    content: T
    status: int


@dataclass(slots=True, frozen=True, kw_only=True)
class _ApplicationsListPayload:
    """Wire shape of main's ``ApplicationsList`` — only the fields needed to paginate."""

    items: list[Application]
    total: int
    page: int


def _extract_id(payload: dict[str, Any] | None) -> UUID | None:
    """Pull ``id`` out of an optional organizer/participant sub-object."""
    if payload is None:
        return None
    return UUID(payload["id"])


_retort = Retort(
    recipe=[
        name_mapping(
            User,
            map={
                "organizer_id": "organizer",
                "participant_id": "participant",
            },
            extra_in=ExtraSkip(),
        ),
        loader(P[User].organizer_id, _extract_id),
        loader(P[User].participant_id, _extract_id),
        name_mapping(ApplicationForm, extra_in=ExtraSkip()),
        name_mapping(ApplicationFormField, extra_in=ExtraSkip()),
        name_mapping(Application, extra_in=ExtraSkip()),
        name_mapping(Participant, extra_in=ExtraSkip()),
    ],
)


class DreamTeamsApiClient:
    """Exporter-local client for calls to the main DreamTeams API."""

    def __init__(self, session: aiohttp.ClientSession, config: DreamteamsApiConfig) -> None:
        self._session = session
        self._config = config

    async def get_me(self, user_id: AuthUserId) -> DreamTeamsApiResponse[User]:
        """Fetch the current user projection from main's ``GET /users/me``."""
        response = await self._get_json("/users/me", user_id)
        return DreamTeamsApiResponse(content=_retort.load(response.content, User), status=response.status)

    async def get_application_form(
        self,
        user_id: AuthUserId,
        competition_id: CompetitionId,
    ) -> DreamTeamsApiResponse[ApplicationForm | None]:
        """Fetch a competition's application form definition from the main API."""
        path = f"/competitions/{competition_id}/application-form/"
        response = await self._get(path, user_id)
        if response.status == _HTTP_NOT_FOUND:
            payload: Any = await response.json()
            if isinstance(payload, dict) and payload.get("code") == "APPLICATION_FORM_NOT_FOUND":
                return DreamTeamsApiResponse(content=None, status=response.status)

        self._raise_for_status(response)
        payload = await response.json()
        return DreamTeamsApiResponse(content=_retort.load(payload, ApplicationForm), status=response.status)

    async def list_applications(
        self,
        user_id: AuthUserId,
        *,
        competition_id: CompetitionId,
        status: ApplicationStatus | None,
        page: int,
        page_size: int,
    ) -> DreamTeamsApiResponse[ApplicationsPage]:
        """Fetch one page of submitted applications from the main API."""
        path = f"/competitions/{competition_id}/applications/"
        params: dict[str, str | int] = {
            "page": page,
            "page_size": page_size,
        }
        if status is not None:
            params["status"] = status.value

        response = await self._get_json(path, user_id, params=params)
        parsed = _retort.load(response.content, _ApplicationsListPayload)
        return DreamTeamsApiResponse(
            content=ApplicationsPage(
                items=parsed.items,
                page=parsed.page,
                page_size=page_size,
                total=parsed.total,
            ),
            status=response.status,
        )

    async def _get_json(
        self,
        path: str,
        user_id: AuthUserId,
        *,
        params: dict[str, str | int] | None = None,
    ) -> DreamTeamsApiResponse[Any]:
        """GET a JSON response, applying retries and status handling."""
        response = await self._get(path, user_id, params=params)
        self._raise_for_status(response)
        return DreamTeamsApiResponse(content=await response.json(), status=response.status)

    async def _get(
        self,
        path: str,
        user_id: AuthUserId,
        *,
        params: dict[str, str | int] | None = None,
    ) -> aiohttp.ClientResponse:
        """Issue an idempotent GET, retrying transient transport and upstream failures."""
        attempts = max(1, self._config.retry_attempts)
        for attempt in range(1, attempts + 1):
            try:
                response = await self._session.get(
                    f"{self._config.base_url}{path}",
                    headers={self._config.auth_header_name: user_id},
                    params=params,
                )
            except (TimeoutError, aiohttp.ClientError):
                if attempt == attempts:
                    raise
                await self._sleep_before_retry(attempt)
                continue

            if response.status not in _RETRYABLE_HTTP_STATUSES or attempt == attempts:
                return response

            response.release()
            await self._sleep_before_retry(attempt)

        msg = "Retry loop exhausted unexpectedly"
        raise RuntimeError(msg)

    async def _sleep_before_retry(self, attempt: int) -> None:
        """Sleep with capped exponential backoff before the next retry attempt."""
        delay = min(
            self._config.retry_backoff_max_seconds,
            self._config.retry_backoff_base_seconds * (2 ** (attempt - 1)),
        )
        if delay > 0:
            await asyncio.sleep(delay)

    @staticmethod
    def _raise_for_status(response: aiohttp.ClientResponse) -> None:
        """Raise exporter/domain errors for known auth failures, else delegate to aiohttp."""
        if response.status in _HTTP_UNAUTHORIZED:
            response.release()
            raise UnauthorizedError
        response.raise_for_status()
