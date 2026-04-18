from abc import abstractmethod
from typing import Protocol

from dreamteams.entities.common.identifiers import UserId
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
        """Return the participant attached to the given user, or None if no participant role exists.

        Skills and contacts are only eager-loaded when ``eager_skills_and_contacts=True``;
        accessing them on the returned entity without this flag raises ``StatementError``
        because both collections are mapped with ``lazy='raise_on_sql'``.
        """
        raise NotImplementedError
