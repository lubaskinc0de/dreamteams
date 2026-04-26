from abc import abstractmethod
from typing import Protocol

from dreamteams.entities.common.identifiers import ParticipantId, UserId
from dreamteams.entities.user import Participant


class ParticipantGateway(Protocol):
    """Gateway for reading participant profiles from persistent storage."""

    @abstractmethod
    async def get_by_user_id(
        self,
        user_id: UserId,
        *,
        eager_skills_and_contacts: bool = False,
    ) -> Participant | None:
        """Return the participant attached to the given user.

        Returns None if no participant role exists or if the user account is blocked.
        Implementations must return None when the user has ``ban_status.is_blocked = True``.

        Skills and contacts are only eager-loaded when ``eager_skills_and_contacts=True``;
        accessing them on the returned entity without this flag raises ``StatementError``
        because both collections are mapped with ``lazy='raise_on_sql'``.
        """
        raise NotImplementedError

    @abstractmethod
    async def get(
        self,
        participant_id: ParticipantId,
        *,
        eager_skills_and_contacts: bool = False,
    ) -> Participant | None:
        """Return the participant by their entity ID.

        Returns None if not found or if the participant's user account is blocked.
        Implementations must return None when the user has ``ban_status.is_blocked = True``.

        Skills and contacts are only eager-loaded when ``eager_skills_and_contacts=True``.
        """
        raise NotImplementedError
