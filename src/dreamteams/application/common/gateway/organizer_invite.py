from abc import abstractmethod
from typing import Protocol

from dreamteams.entities.common.identifiers import OrganizerInviteId, UserId
from dreamteams.entities.organizer_invite import OrganizerInvite


class OrganizerInviteGateway(Protocol):
    """Gateway for managing organizer invite codes."""

    @abstractmethod
    async def get_by_id(self, invite_id: OrganizerInviteId) -> OrganizerInvite | None:
        """Retrieve an invite by its UUID primary key."""
        raise NotImplementedError

    @abstractmethod
    async def get_by_code(self, code: str) -> OrganizerInvite | None:
        """Retrieve an invite by its unique code string."""
        raise NotImplementedError

    @abstractmethod
    async def list(
        self,
        *,
        created_by: UserId,
        page: int,
        page_size: int,
    ) -> tuple[list[OrganizerInvite], int]:
        """
        List invites created by a specific admin user, ordered by created_at DESC.

        Returns tuple of (invites list, total count).
        """
        raise NotImplementedError
