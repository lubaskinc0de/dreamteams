from abc import abstractmethod
from typing import Protocol

from dreamteams.entities.common.identifiers import UserId
from dreamteams.entities.user import Participant


class ParticipantGateway(Protocol):
    """Gateway for reading participant profiles from persistent storage."""

    @abstractmethod
    async def get_by_user_id(self, user_id: UserId) -> Participant | None:
        """Return the participant attached to the given user, or None if no participant role exists."""
        raise NotImplementedError
