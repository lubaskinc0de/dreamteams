from typing import override

import structlog

from dreamteams.adapters.auth.common.gateway.auth_user import AuthUserGateway
from dreamteams.adapters.auth.errors.base import UnauthorizedError, UnauthorizedReason
from dreamteams.adapters.auth.idp.base import AuthUserIdProvider
from dreamteams.application.common.idp import IdProvider
from dreamteams.application.common.logger import Logger
from dreamteams.entities.user import User

logger: Logger = structlog.get_logger(__name__)


class IdProviderImpl(IdProvider):
    """Adapter implementation that resolves application User entity from authentication user ID."""

    def __init__(self, idp: AuthUserIdProvider, gateway: AuthUserGateway) -> None:
        self._idp = idp
        self._gateway = gateway
        self._cached_user: User | None = None

    async def _get_user(self) -> User:
        """Resolves the authenticated user by looking up the auth user ID.

        returning the associated application user and caching it.
        """
        if self._cached_user is not None:
            return self._cached_user

        auth_user_id = await self._idp.get_auth_user_id()
        if (auth_user := await self._gateway.get(auth_user_id)) is None:
            logger.info("Request unauthorized due to auth user is not exists", auth_user_id=auth_user_id)
            raise UnauthorizedError(reason=UnauthorizedReason.INVALID_AUTH_USER_ID)

        self._cached_user = auth_user.user
        return self._cached_user

    @override
    async def get_user(self) -> User:
        """Resolves the authenticated user by looking up the auth user ID.

        and returning the associated application user.
        """
        return await self._get_user()

    @override
    async def get_user_or_none(self) -> User | None:
        """Resolves the authenticated user by looking up the auth user ID.

        and returning the associated application user or None.
        """
        try:
            return await self._get_user()
        except UnauthorizedError:
            logger.debug("Unauthorized error", exc_info=True)
            return None
