from typing import Any
from uuid import UUID

import aiohttp
from adaptix import ExtraSkip, P, Retort, loader, name_mapping

from dreamteams_exporter.adapters.http.config import DreamteamsApiConfig
from dreamteams_exporter.application.errors.auth import UnauthorizedError
from dreamteams_exporter.entities.user import User


def _extract_id(payload: dict[str, Any] | None) -> UUID | None:
    """Pulls ``id`` out of an optional organizer/participant sub-object."""
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
    ],
)


class HttpUserGateway:
    """Adapter-internal helper that fetches the current User from main's ``GET /users/me``.

    Used by both ``HttpIdProvider`` and ``MessageIdProvider``. Not exposed as an application-layer
    protocol — the application layer only knows ``IdProvider``.
    """

    def __init__(self, session: aiohttp.ClientSession, config: DreamteamsApiConfig) -> None:
        self._session = session
        self._config = config

    async def get_me(self, auth_token: str) -> User:
        """Issues ``GET {base}/users/me`` with the caller's ``X-Auth-User`` header forwarded verbatim."""
        url = f"{self._config.base_url}/users/me"
        headers = {self._config.auth_header_name: auth_token}

        async with self._session.get(url, headers=headers) as response:
            if response.status in (401, 403):
                raise UnauthorizedError
            response.raise_for_status()
            payload = await response.json()

        return _retort.load(payload, User)
