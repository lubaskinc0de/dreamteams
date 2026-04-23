from typing import override

from faststream.nats import NatsMessage

from dreamteams_exporter.adapters.http.config import DreamteamsApiConfig
from dreamteams_exporter.adapters.http.user_gateway import HttpUserGateway
from dreamteams_exporter.application.common.idp import IdProvider
from dreamteams_exporter.application.errors.auth import UnauthorizedError
from dreamteams_exporter.entities.user import User


class MessageIdProvider(IdProvider):
    """IdProvider for the FastStream worker — reads X-Auth-User from the NATS message headers."""

    def __init__(
        self,
        message: NatsMessage,
        user_gateway: HttpUserGateway,
        api_config: DreamteamsApiConfig,
    ) -> None:
        self._message = message
        self._user_gateway = user_gateway
        self._header_name = api_config.auth_header_name
        self._cached: User | None = None

    @override
    async def get_user(self) -> User:
        """Returns the authenticated User; raises UnauthorizedError when no header is attached."""
        if self._cached is not None:
            return self._cached

        token = self._message.headers.get(self._header_name) if self._message.headers else None
        if token is None:
            raise UnauthorizedError

        self._cached = await self._user_gateway.get_me(token)
        return self._cached
