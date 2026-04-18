from abc import abstractmethod
from typing import Protocol

from dreamteams.adapters.auth.model import AuthUserId
from dreamteams.entities.common.identifiers import UserId


class AuthUserCache(Protocol):
    """Cache for the immutable ``auth_user_id -> user_id`` mapping resolved by IdProvider.

    Positive-only (misses are not cached). Cache failures must be swallowed by the
    implementation so request handling never depends on cache availability. Staleness
    is bounded by TTL; no invalidation path because the cached mapping is effectively
    immutable (AuthUser.user_id is set at registration and never updated) and stale
    entries pointing at deleted users degrade to correct downstream 404s via the
    existing UserNotFoundError path.
    """

    @abstractmethod
    async def get_user_id(self, auth_user_id: AuthUserId) -> UserId | None:
        """Return the cached user_id for the given auth_user_id, or None on miss or error."""
        raise NotImplementedError

    @abstractmethod
    async def set_user_id(self, auth_user_id: AuthUserId, user_id: UserId) -> None:
        """Cache the mapping; errors are swallowed."""
        raise NotImplementedError
