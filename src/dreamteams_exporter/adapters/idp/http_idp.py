from typing import override

from fastapi import Request

from dreamteams_exporter.adapters.http.config import DreamteamsApiConfig
from dreamteams_exporter.adapters.http.user_gateway import HttpUserGateway
from dreamteams_exporter.application.common.idp import IdProvider
from dreamteams_exporter.application.errors.auth import UnauthorizedError
from dreamteams_exporter.entities.user import User


class HttpIdProvider(IdProvider):
    """IdProvider for HTTP."""

    def __init__(
        self,
        request: Request,
        user_gateway: HttpUserGateway,
        api_config: DreamteamsApiConfig,
    ) -> None:
        self._request = request
        self._user_gateway = user_gateway
        self._header_name = api_config.auth_header_name
        self._cached: User | None = None

    @override
    async def get_user(self) -> User:
        """Returns the authenticated User; raises UnauthorizedError when no header is attached."""
        if self._cached is not None:
            return self._cached

        token = self._request.headers.get(self._header_name)
        if token is None:
            raise UnauthorizedError

        self._cached = await self._user_gateway.get_me(token)
        return self._cached
