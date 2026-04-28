import json
from typing import Any, cast, override

import structlog
from adaptix import Retort
from adaptix.load_error import LoadError
from redis.asyncio import Redis
from redis.exceptions import RedisError

from dreamteams.adapters.cache.competition_read_cache import CompetitionReadCache
from dreamteams.adapters.cache.config import CacheConfig
from dreamteams.application.common.competition_cache import CompetitionCache
from dreamteams.application.common.dto.competition import CompetitionModel
from dreamteams.application.common.dto.preview_competition import PreviewCompetitionModel
from dreamteams.entities.common.identifiers import CompetitionId
from dreamteams_common.logger import Logger

_READ_KEY_PREFIX = "competition:read:"
_PREVIEW_KEY_PREFIX = "competitions:preview:"
_retort = Retort()
logger: Logger = structlog.get_logger(__name__)


def _read_key(competition_id: CompetitionId) -> str:
    return f"{_READ_KEY_PREFIX}{competition_id}"


def _preview_key(*, page: int, page_size: int) -> str:
    return f"{_PREVIEW_KEY_PREFIX}{page}:{page_size}"


def _to_text(raw: bytes | str) -> str:
    if isinstance(raw, bytes):
        return raw.decode()
    return raw


def _load_competition_model(payload: dict[str, Any]) -> CompetitionModel:
    return _retort.load(payload, CompetitionModel)


def _dump_competition_model(model: CompetitionModel) -> dict[str, Any]:
    return cast("dict[str, Any]", _retort.dump(model))


def _dump_preview_model(model: PreviewCompetitionModel) -> dict[str, Any]:
    return cast("dict[str, Any]", _retort.dump(model))


def _load_preview_models(payload: list[Any]) -> list[PreviewCompetitionModel]:
    return _retort.load(payload, list[PreviewCompetitionModel])


class RedisCompetitionCache(CompetitionCache, CompetitionReadCache):
    """Redis cache for competition read models."""

    def __init__(self, redis: Redis, config: CacheConfig) -> None:
        self._redis = redis
        self._config = config

    @override
    async def get_read(self, competition_id: CompetitionId) -> CompetitionModel | None:
        """Return a cached single-competition read model, or None on miss/error."""
        try:
            raw = await self._redis.get(_read_key(competition_id))
        except RedisError:
            logger.warning("competition_cache read failed", exc_info=True, competition_id=competition_id)
            return None

        if raw is None:
            return None

        try:
            payload = json.loads(_to_text(raw))
            if not isinstance(payload, dict):
                return None
            return _load_competition_model(payload)
        except (json.JSONDecodeError, LoadError, TypeError, UnicodeDecodeError, ValueError):
            logger.warning("competition_cache read hit but value is malformed", competition_id=competition_id, raw=raw)
            return None

    @override
    async def set_read(self, competition_id: CompetitionId, model: CompetitionModel) -> None:
        """Store a single-competition read model."""
        try:
            await self._redis.set(
                _read_key(competition_id),
                json.dumps(_dump_competition_model(model)),
                ex=self._config.competition_read_ttl_seconds,
            )
        except RedisError:
            logger.warning("competition_cache read write failed", exc_info=True, competition_id=competition_id)

    @override
    async def delete_read(self, competition_id: CompetitionId) -> None:
        """Delete one single-competition read model entry."""
        try:
            await self._redis.delete(_read_key(competition_id))
        except RedisError:
            logger.warning("competition_cache read delete failed", exc_info=True, competition_id=competition_id)

    @override
    async def clear_read(self) -> None:
        """Clear all single-competition read model entries."""
        await self._delete_pattern(f"{_READ_KEY_PREFIX}*", "read_clear")

    @override
    async def get_preview(self, *, page: int, page_size: int) -> tuple[list[PreviewCompetitionModel], int] | None:
        """Return a cached anonymous preview page, or None on miss/error."""
        try:
            raw = await self._redis.get(_preview_key(page=page, page_size=page_size))
        except RedisError:
            logger.warning("competition_cache preview read failed", exc_info=True, page=page)
            return None

        if raw is None:
            return None

        try:
            payload = json.loads(_to_text(raw))
            if not isinstance(payload, dict) or not isinstance(payload.get("items"), list):
                return None
            items = _load_preview_models(payload["items"])
            return items, int(payload["total"])
        except (json.JSONDecodeError, LoadError, TypeError, UnicodeDecodeError, ValueError):
            logger.warning("competition_cache preview hit but value is malformed", page=page, raw=raw)
            return None

    @override
    async def set_preview(self, *, page: int, page_size: int, items: list[PreviewCompetitionModel], total: int) -> None:
        """Store an anonymous preview page."""
        payload: dict[str, Any] = {
            "items": [_dump_preview_model(item) for item in items],
            "total": total,
        }
        try:
            await self._redis.set(
                _preview_key(page=page, page_size=page_size),
                json.dumps(payload),
                ex=self._config.competition_preview_ttl_seconds,
            )
        except RedisError:
            logger.warning("competition_cache preview write failed", exc_info=True, page=page)

    @override
    async def clear_preview(self) -> None:
        """Clear every anonymous preview page entry."""
        await self._delete_pattern(f"{_PREVIEW_KEY_PREFIX}*", "preview_clear")

    async def _delete_pattern(self, pattern: str, operation: str) -> None:
        try:
            keys = [key async for key in self._redis.scan_iter(match=pattern)]
            if keys:
                await self._redis.delete(*keys)
        except RedisError:
            logger.warning("competition_cache %s failed", operation, exc_info=True)
