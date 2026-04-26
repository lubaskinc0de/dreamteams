from typing import override

import structlog
from opentelemetry import trace

from dreamteams.adapters.auth.common.gateway.auth_user import AuthUserGateway
from dreamteams.adapters.auth.errors.base import UnauthorizedError, UnauthorizedReason
from dreamteams.adapters.auth.idp.base import AuthUserIdProvider
from dreamteams.adapters.cache.auth_user_cache import AuthUserCache
from dreamteams.adapters.cache.blocked_user_cache import BlockedUserCache  # adapter read+write protocol
from dreamteams.application.common.gateway.user import UserGateway
from dreamteams.application.common.idp import IdProvider
from dreamteams.application.common.logger import Logger
from dreamteams.application.errors.user import UserBlockedError
from dreamteams.entities.common.identifiers import UserId

_tracer = trace.get_tracer("dreamteams.adapters")

logger: Logger = structlog.get_logger(__name__)


class IdProviderImpl(IdProvider):
    """Adapter that resolves the application UserId from the request authentication context."""

    def __init__(
        self,
        idp: AuthUserIdProvider,
        gateway: AuthUserGateway,
        cache: AuthUserCache,
        blocked_cache: BlockedUserCache,
        user_gateway: UserGateway,
    ) -> None:
        self._idp = idp
        self._gateway = gateway
        self._cache = cache
        self._blocked_cache = blocked_cache
        self._user_gateway = user_gateway
        self._cached_user_id: UserId | None = None

    async def _resolve_user_id(self) -> UserId:
        if self._cached_user_id is not None:
            return self._cached_user_id

        with _tracer.start_as_current_span("auth.idp_resolve_user"):
            auth_user_id = await self._idp.get_auth_user_id()

            with _tracer.start_as_current_span("auth.idp_cache_lookup"):
                cached_user_id = await self._cache.get_user_id(auth_user_id)
            if cached_user_id is not None:
                self._cached_user_id = cached_user_id
            else:
                with _tracer.start_as_current_span("auth.idp_fetch_user"):
                    auth_user = await self._gateway.get(auth_user_id)
                    if auth_user is None:
                        logger.info("Request unauthorized due to auth user is not exists", auth_user_id=auth_user_id)
                        raise UnauthorizedError(reason=UnauthorizedReason.INVALID_AUTH_USER_ID)

                await self._cache.set_user_id(auth_user_id, auth_user.user_id)
                self._cached_user_id = auth_user.user_id

            await self._check_not_blocked(self._cached_user_id)
            return self._cached_user_id

    async def _check_not_blocked(self, user_id: UserId) -> None:
        with _tracer.start_as_current_span("auth.idp_blocked_check"):
            ban_status = await self._blocked_cache.get_ban_status(user_id)
            if ban_status is None:
                user = await self._user_gateway.get(user_id)
                if user is not None and user.ban_status.is_blocked:
                    await self._blocked_cache.set_blocked(user_id, user.ban_status)
                    ban_status = user.ban_status
            if ban_status is not None:
                raise UserBlockedError(reason=ban_status.reason, blocked_at=ban_status.blocked_at)

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
