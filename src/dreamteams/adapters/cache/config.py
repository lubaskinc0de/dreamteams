from dataclasses import dataclass


@dataclass(slots=True, frozen=True, kw_only=True)
class CacheConfig:
    """Redis cache configuration loaded from the ``[cache]`` TOML section."""

    url: str
    # TTL for IdP auth_user_id -> user_id entries. Jitter is added at write time to
    # avoid a synchronised stampede of expirations.
    auth_user_ttl_seconds: int
    auth_user_ttl_jitter_seconds: int
    # TTL for blocked-user cache entries. Entries are only written on block, deleted on unblock.
    blocked_user_ttl_seconds: int
    # TTL for competition application form entries.
    application_form_ttl_seconds: int
    # TTL for competition tag entries and list pages.
    competition_tags_ttl_seconds: int
    # TTL for single competition read models.
    competition_read_ttl_seconds: int
