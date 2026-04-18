from dataclasses import dataclass


@dataclass(slots=True, frozen=True, kw_only=True)
class CacheConfig:
    """Redis cache configuration loaded from the ``[cache]`` TOML section."""

    url: str
    # TTL for IdP auth_user_id -> user_id entries. Jitter is added at write time to
    # avoid a synchronised stampede of expirations.
    auth_user_ttl_seconds: int
    auth_user_ttl_jitter_seconds: int
