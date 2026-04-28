import json
from typing import Any, cast, override

import structlog
from adaptix import Retort, dumper, loader
from adaptix.load_error import LoadError
from redis.asyncio import Redis
from redis.exceptions import RedisError

from dreamteams.adapters.cache.config import CacheConfig
from dreamteams.application.common.application_form_cache import ApplicationFormCache
from dreamteams.entities.application_form.entity import ApplicationForm
from dreamteams.entities.application_form.field import Field
from dreamteams.entities.application_form.fields import ApplicationFormFields
from dreamteams.entities.common.identifiers import CompetitionId
from dreamteams_common.logger import Logger

_KEY_PREFIX = "application_form:"
_field_retort = Retort()
logger: Logger = structlog.get_logger(__name__)


def _key(competition_id: CompetitionId) -> str:
    return f"{_KEY_PREFIX}{competition_id}"


def _to_text(raw: bytes | str) -> str:
    if isinstance(raw, bytes):
        return raw.decode()
    return raw


def _dump_fields(fields: ApplicationFormFields) -> list[Any]:
    return [_field_retort.dump(field) for field in fields]


def _load_fields(items: list[Any]) -> ApplicationFormFields:
    return ApplicationFormFields([_field_retort.load(item, Field) for item in items])


_retort = Retort(
    recipe=[
        dumper(ApplicationFormFields, _dump_fields),
        loader(ApplicationFormFields, _load_fields),
    ],
)


def _dump_form(form: ApplicationForm) -> dict[str, Any]:
    return cast("dict[str, Any]", _retort.dump(form))


def _load_form(payload: dict[str, Any]) -> ApplicationForm:
    return _retort.load(payload, ApplicationForm)


class RedisApplicationFormCache(ApplicationFormCache):
    """Redis cache for application forms."""

    def __init__(self, redis: Redis, config: CacheConfig) -> None:
        self._redis = redis
        self._config = config

    @override
    async def get(self, competition_id: CompetitionId) -> ApplicationForm | None:
        """Return cached form for the competition, or None on miss/error."""
        try:
            raw = await self._redis.get(_key(competition_id))
        except RedisError:
            logger.warning("application_form_cache read failed", exc_info=True, competition_id=competition_id)
            return None

        if raw is None:
            return None

        try:
            payload = json.loads(_to_text(raw))
            if not isinstance(payload, dict):
                return None
            return _load_form(payload)
        except (json.JSONDecodeError, LoadError, TypeError, UnicodeDecodeError, ValueError):
            logger.warning("application_form_cache hit but value is malformed", competition_id=competition_id, raw=raw)
            return None

    @override
    async def set(self, competition_id: CompetitionId, form: ApplicationForm) -> None:
        """Store a form for the competition."""
        try:
            await self._redis.set(
                _key(competition_id),
                json.dumps(_dump_form(form)),
                ex=self._config.application_form_ttl_seconds,
            )
        except RedisError:
            logger.warning("application_form_cache write failed", exc_info=True, competition_id=competition_id)

    @override
    async def delete(self, competition_id: CompetitionId) -> None:
        """Delete one competition form cache entry."""
        try:
            await self._redis.delete(_key(competition_id))
        except RedisError:
            logger.warning("application_form_cache delete failed", exc_info=True, competition_id=competition_id)

    @override
    async def clear(self) -> None:
        """Clear every application form cache entry."""
        try:
            keys = [key async for key in self._redis.scan_iter(match=f"{_KEY_PREFIX}*")]
            if keys:
                await self._redis.delete(*keys)
        except RedisError:
            logger.warning("application_form_cache clear failed", exc_info=True)
