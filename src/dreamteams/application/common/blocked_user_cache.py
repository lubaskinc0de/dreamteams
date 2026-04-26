from abc import abstractmethod
from typing import Protocol

from dreamteams.entities.common.identifiers import UserId
from dreamteams.entities.user import BanStatus


class BlockedUserCache(Protocol):
    """Write interface for the blocked-user cache.

    Used by application-layer interactors to update the cache on block/unblock.
    Implementations must swallow errors so cache failures never break requests.
    """

    @abstractmethod
    async def set_blocked(self, user_id: UserId, ban_status: BanStatus) -> None:
        """Cache the ban status for a blocked user. Errors are swallowed."""
        raise NotImplementedError

    @abstractmethod
    async def delete(self, user_id: UserId) -> None:
        """Remove the user from the blocked cache (called on unblock). Errors are swallowed."""
        raise NotImplementedError
