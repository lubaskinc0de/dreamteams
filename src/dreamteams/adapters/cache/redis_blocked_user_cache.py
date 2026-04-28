import json
from typing import override

import structlog
from adaptix import Retort
from adaptix.load_error import LoadError
from redis.asyncio import Redis
from redis.exceptions import RedisError

from dreamteams.adapters.cache.blocked_user_cache import BlockedUserCache  # full read+write protocol
from dreamteams.adapters.cache.config import CacheConfig
from dreamteams.entities.common.identifiers import UserId
from dreamteams.entities.user import BanStatus
from dreamteams_common.logger import Logger

_KEY_PREFIX = "idp:blocked:"
_retort = Retort()
logger: Logger = structlog.get_logger(__name__)


def _key(user_id: UserId) -> str:
    return f"{_KEY_PREFIX}{user_id}"


class RedisBlockedUserCache(BlockedUserCache):
    """
    Redis-backed positive-only cache storing blocked user ban details as JSON.

    Failures (connection, timeout, deserialisation) are logged and swallowed so a
    degraded cache never turns into a failed request.
    """

    def __init__(self, redis: Redis, config: CacheConfig) -> None:
        self._redis = redis
        self._config = config

    @override
    async def get_ban_status(self, user_id: UserId) -> BanStatus | None:
        """Return BanStatus if cached as blocked, None on miss or error."""
        try:
            raw = await self._redis.get(_key(user_id))
        except RedisError:
            logger.warning("blocked_user_cache read failed", exc_info=True, user_id=user_id)
            return None
        if raw is None:
            return None
        try:
            return _retort.load(json.loads(raw), BanStatus)
        except (json.JSONDecodeError, LoadError, TypeError, UnicodeDecodeError):
            logger.warning("blocked_user_cache hit but value is malformed", user_id=user_id, raw=raw)
            return None

    @override
    async def set_blocked(self, user_id: UserId, ban_status: BanStatus) -> None:
        """Cache the ban status with configured TTL. Errors are swallowed."""
        try:
            payload = json.dumps(_retort.dump(ban_status))
            await self._redis.set(_key(user_id), payload, ex=self._config.blocked_user_ttl_seconds)
        except RedisError:
            logger.warning("blocked_user_cache write failed", exc_info=True, user_id=user_id)

    @override
    async def delete(self, user_id: UserId) -> None:
        """Remove the user from the blocked cache. Errors are swallowed."""
        try:
            await self._redis.delete(_key(user_id))
        except RedisError:
            logger.warning("blocked_user_cache delete failed", exc_info=True, user_id=user_id)
