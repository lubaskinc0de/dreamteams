from typing import override

import structlog
from opentelemetry import trace

from dreamteams.adapters.auth.common.gateway.auth_user import AuthUserGateway
from dreamteams.adapters.auth.errors.base import UnauthorizedError, UnauthorizedReason
from dreamteams.adapters.auth.idp.base import AuthUserIdProvider
from dreamteams.application.common.idp import IdProvider
from dreamteams.application.common.logger import Logger
from dreamteams.entities.common.identifiers import UserId

_tracer = trace.get_tracer("dreamteams.adapters")

logger: Logger = structlog.get_logger(__name__)


class IdProviderImpl(IdProvider):
    """Adapter that resolves the application UserId from the request authentication context."""

    def __init__(self, idp: AuthUserIdProvider, gateway: AuthUserGateway) -> None:
        self._idp = idp
        self._gateway = gateway
        self._cached_user_id: UserId | None = None

    async def _resolve_user_id(self) -> UserId:
        if self._cached_user_id is not None:
            return self._cached_user_id

        with _tracer.start_as_current_span("auth.idp_resolve_user"):
            auth_user_id = await self._idp.get_auth_user_id()

            with _tracer.start_as_current_span("auth.idp_fetch_user"):
                auth_user = await self._gateway.get(auth_user_id)
                if auth_user is None:
                    logger.info("Request unauthorized due to auth user is not exists", auth_user_id=auth_user_id)
                    raise UnauthorizedError(reason=UnauthorizedReason.INVALID_AUTH_USER_ID)

            self._cached_user_id = auth_user.user_id
            return self._cached_user_id

    @override
    async def get_user_id(self) -> UserId:
        """Resolves the authenticated user id; raises ``UnauthorizedError`` when no auth context exists."""
        user_id = await self._resolve_user_id()
        trace.get_current_span().set_attribute("user.id", str(user_id))
        return user_id

    @override
    async def get_user_id_or_none(self) -> UserId | None:
        """Resolves the authenticated user id, returning ``None`` if the request is unauthenticated."""
        try:
            return await self._resolve_user_id()
        except UnauthorizedError:
            logger.debug("Unauthorized error", exc_info=True)
            return None
