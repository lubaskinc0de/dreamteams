from typing import Any, override

from faststream.message import StreamMessage

from dreamteams_exporter.adapters.auth.model import AuthUserId
from dreamteams_exporter.adapters.http.config import DreamteamsApiConfig
from dreamteams_exporter.adapters.http.user_gateway import HttpUserGateway
from dreamteams_exporter.application.common.idp import IdProvider
from dreamteams_exporter.application.errors.auth import UnauthorizedError
from dreamteams_exporter.entities.user import User


class MessageIdProvider(IdProvider):
    """
    IdProvider for the NATS worker entry point.

    Reads the caller id from the inbound message headers on construction and caches the resolved
    User for the message lifetime.
    """

    def __init__(
        self,
        message: StreamMessage[Any],
        user_gateway: HttpUserGateway,
        api_config: DreamteamsApiConfig,
    ) -> None:
        token = message.headers.get(api_config.auth_header_name) if message.headers else None
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
