from typing import override

from fastapi import Request

from dreamteams_exporter.adapters.auth.model import AuthUserId
from dreamteams_exporter.adapters.http.config import DreamteamsApiConfig
from dreamteams_exporter.adapters.http.user_gateway import HttpUserGateway
from dreamteams_exporter.application.common.idp import IdProvider
from dreamteams_exporter.application.errors.auth import UnauthorizedError
from dreamteams_exporter.entities.user import User


class HttpIdProvider(IdProvider):
    """IdProvider for the HTTP entry point.

    Reads the caller id from the configured auth header on construction and caches the resolved
    User for the request lifetime.
    """

    def __init__(
        self,
        request: Request,
        user_gateway: HttpUserGateway,
        api_config: DreamteamsApiConfig,
    ) -> None:
        token = request.headers.get(api_config.auth_header_name)
        if token is None:
            raise UnauthorizedError

        self.user_id: AuthUserId = token
        self._user_gateway = user_gateway
        self._cached: User | None = None

    @override
    async def get_user(self) -> User:
        """Returns the authenticated User, fetching it from upstream on first call."""
        if self._cached is not None:
            return self._cached

        self._cached = await self._user_gateway.get_me(self.user_id)
        return self._cached
