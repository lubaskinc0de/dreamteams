from abc import abstractmethod
from typing import Protocol

from dreamteams.application.common.blocked_user_cache import BlockedUserCache as BlockedUserCacheBase
from dreamteams.entities.common.identifiers import UserId
from dreamteams.entities.user import BanStatus


class BlockedUserCache(BlockedUserCacheBase, Protocol):
    """
    Full read+write interface for the blocked-user cache.

    Extends the application-level write interface with the read method used by
    IdProviderImpl to check blocked status on each request.
    """

    @abstractmethod
    async def get_ban_status(self, user_id: UserId) -> BanStatus | None:
        """Return BanStatus(is_blocked=True, ...) if cached, None on miss or error."""
        raise NotImplementedError
