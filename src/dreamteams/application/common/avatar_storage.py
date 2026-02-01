from abc import abstractmethod
from typing import BinaryIO, Protocol

from dreamteams.entities.common.identifiers import UserId


class AvatarStorage(Protocol):
    """Storage for user avatar management."""

    @abstractmethod
    async def upload_avatar(
        self,
        user_id: UserId,
        file_data: BinaryIO,
        content_type: str,
    ) -> str:
        """Upload user avatar to storage."""

    @abstractmethod
    async def delete_avatar(self, user_id: UserId) -> None:
        """Delete user avatar from storage."""
