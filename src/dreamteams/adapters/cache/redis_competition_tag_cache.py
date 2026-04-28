import json
from typing import Any, cast, override

import structlog
from adaptix import Retort
from adaptix.load_error import LoadError
from redis.asyncio import Redis
from redis.exceptions import RedisError

from dreamteams.adapters.cache.competition_tag_read_cache import CompetitionTagReadCache
from dreamteams.adapters.cache.config import CacheConfig
from dreamteams.application.common.competition_tag_cache import CompetitionTagCache
from dreamteams.entities.competition.tag import CompetitionTag
from dreamteams_common.logger import Logger

_KEY_PREFIX = "tags:"
_retort = Retort()
logger: Logger = structlog.get_logger(__name__)


def _value_key(value: str) -> str:
    return f"{_KEY_PREFIX}value:{_normalize_value(value)}"


def _list_key(*, page: int, page_size: int, search: str | None) -> str:
    normalized_search = search.strip().lower() if search is not None else ""
    return f"{_KEY_PREFIX}list:{page}:{page_size}:{normalized_search}"


def _normalize_value(value: str) -> str:
    return value.strip().lower()


def _to_text(raw: bytes | str) -> str:
    if isinstance(raw, bytes):
        return raw.decode()
    return raw


def _dump_tag(tag: CompetitionTag) -> dict[str, Any]:
    return cast("dict[str, Any]", _retort.dump(tag))


def _load_tag(payload: dict[str, Any]) -> CompetitionTag:
    return _retort.load(payload, CompetitionTag)


def _load_tags(payload: list[Any]) -> list[CompetitionTag]:
    return _retort.load(payload, list[CompetitionTag])


class RedisCompetitionTagCache(CompetitionTagCache, CompetitionTagReadCache):
    """Redis cache for competition tags."""

    def __init__(self, redis: Redis, config: CacheConfig) -> None:
        self._redis = redis
        self._config = config

    @override
    async def get_by_value(self, value: str) -> CompetitionTag | None:
        """Return a cached tag by normalized value, or None on miss/error."""
        return await self._get_tag(_value_key(value), operation="value_read", context={"value": value})

    @override
    async def set_by_value(self, value: str, tag: CompetitionTag) -> None:
        """Store a tag by normalized value."""
        await self._set_tag(_value_key(value), tag, operation="value_write", context={"value": value})

    @override
    async def get_list(
        self,
        *,
        page: int,
        page_size: int,
        search: str | None,
    ) -> tuple[list[CompetitionTag], int] | None:
        """Return a cached tag list page, or None on miss/error."""
        try:
            raw = await self._redis.get(_list_key(page=page, page_size=page_size, search=search))
        except RedisError:
            logger.warning("competition_tag_cache list_read failed", exc_info=True, page=page, search=search)
            return None
        if raw is None:
            return None
        try:
            payload = json.loads(_to_text(raw))
            if not isinstance(payload, dict) or not isinstance(payload.get("items"), list):
                return None
            return _load_tags(payload["items"]), int(payload["total"])
        except (json.JSONDecodeError, LoadError, TypeError, UnicodeDecodeError, ValueError):
            logger.warning("competition_tag_cache list hit but value is malformed", page=page, search=search, raw=raw)
            return None

    @override
    async def set_list(
        self,
        *,
        page: int,
        page_size: int,
        search: str | None,
        items: list[CompetitionTag],
        total: int,
    ) -> None:
        """Store a tag list page."""
        try:
            await self._redis.set(
                _list_key(page=page, page_size=page_size, search=search),
                json.dumps({"items": [_dump_tag(item) for item in items], "total": total}),
                ex=self._config.competition_tags_ttl_seconds,
            )
        except RedisError:
            logger.warning("competition_tag_cache list_write failed", exc_info=True, page=page, search=search)

    @override
    async def clear(self) -> None:
        """Clear every tag cache entry."""
        try:
            keys = [key async for key in self._redis.scan_iter(match=f"{_KEY_PREFIX}*")]
            if keys:
                await self._redis.delete(*keys)
        except RedisError:
            logger.warning("competition_tag_cache clear failed", exc_info=True)

    async def _get_tag(self, key: str, *, operation: str, context: dict[str, Any]) -> CompetitionTag | None:
        try:
            raw = await self._redis.get(key)
        except RedisError:
            logger.warning("competition_tag_cache %s failed", operation, exc_info=True, **context)
            return None
        if raw is None:
            return None
        try:
            payload = json.loads(_to_text(raw))
            if not isinstance(payload, dict):
                return None
            return _load_tag(payload)
        except (json.JSONDecodeError, LoadError, TypeError, UnicodeDecodeError, ValueError):
            logger.warning("competition_tag_cache hit but value is malformed", operation=operation, raw=raw, **context)
            return None

    async def _set_tag(self, key: str, tag: CompetitionTag, *, operation: str, context: dict[str, Any]) -> None:
        try:
            await self._redis.set(key, json.dumps(_dump_tag(tag)), ex=self._config.competition_tags_ttl_seconds)
        except RedisError:
            logger.warning("competition_tag_cache %s failed", operation, exc_info=True, **context)
