import random
from typing import override
from uuid import UUID

import structlog
from redis.asyncio import Redis
from redis.exceptions import RedisError

from dreamteams.adapters.auth.model import AuthUserId
from dreamteams.adapters.cache.auth_user_cache import AuthUserCache
from dreamteams.adapters.cache.config import CacheConfig
from dreamteams.entities.common.identifiers import UserId
from dreamteams_common.logger import Logger

_KEY_PREFIX = "idp:auth_user:"
logger: Logger = structlog.get_logger(__name__)


def _key(auth_user_id: AuthUserId) -> str:
    return f"{_KEY_PREFIX}{auth_user_id}"


class RedisAuthUserCache(AuthUserCache):
    """
    Redis-backed implementation of :class:`AuthUserCache`.

    Failures (connection, timeout, deserialisation) are logged and swallowed so a
    degraded cache never turns into a failed request.
    """

    def __init__(self, redis: Redis, config: CacheConfig) -> None:
        self._redis = redis
        self._config = config

    @override
    async def get_user_id(self, auth_user_id: AuthUserId) -> UserId | None:
        """Return cached user_id, or None on miss / Redis error / invalid payload."""
        try:
            raw = await self._redis.get(_key(auth_user_id))
        except RedisError:
            logger.warning("auth_user_cache read failed", exc_info=True, auth_user_id=auth_user_id)
            return None
        if raw is None:
            return None
        try:
            return UUID(raw.decode() if isinstance(raw, bytes) else raw)
        except (ValueError, AttributeError):
            logger.warning("auth_user_cache hit but value is not a UUID", auth_user_id=auth_user_id, raw=raw)
            return None

    @override
    async def set_user_id(self, auth_user_id: AuthUserId, user_id: UserId) -> None:
        """Cache the mapping with jittered TTL. Errors are swallowed."""
        jitter = self._config.auth_user_ttl_jitter_seconds
        ttl = self._config.auth_user_ttl_seconds + (random.randint(-jitter, jitter) if jitter > 0 else 0)  # noqa: S311
        try:
            await self._redis.set(_key(auth_user_id), str(user_id), ex=max(1, ttl))
        except RedisError:
            logger.warning("auth_user_cache write failed", exc_info=True, auth_user_id=auth_user_id)
