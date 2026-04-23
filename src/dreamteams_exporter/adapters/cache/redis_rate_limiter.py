from typing import override

from redis.asyncio import Redis

from dreamteams_exporter.adapters.cache.config import CacheConfig
from dreamteams_exporter.application.common.rate_limiter import ExportRateLimiter
from dreamteams_exporter.application.errors.rate_limit import RateLimitExceededError
from dreamteams_exporter.entities.common.identifiers import UserId


class RedisExportRateLimiter(ExportRateLimiter):
    """Fixed-window rate limiter backed by Redis ``INCR`` + ``EXPIRE``."""

    def __init__(self, redis: Redis, config: CacheConfig) -> None:
        self._redis = redis
        self._config = config

    @override
    async def check_and_record(self, user_id: UserId) -> None:
        """Records one attempt for ``user_id`` and raises when the window's max is exceeded."""
        key = f"exporter:rl:{user_id}"
        count = await self._redis.incr(key)
        if count == 1:
            await self._redis.expire(key, self._config.rate_limit_window_seconds)
        if count > self._config.rate_limit_max:
            raise RateLimitExceededError
