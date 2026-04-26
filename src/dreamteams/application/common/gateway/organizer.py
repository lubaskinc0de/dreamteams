from typing import Protocol

from dreamteams.entities.common.identifiers import UserId
from dreamteams.entities.user import Organizer


class OrganizerGateway(Protocol):
    """Gateway for reading organizer profiles and checking uniqueness."""

    async def get_by_user_id(self, user_id: UserId) -> Organizer | None:
        """Return the organizer attached to the given user.

        Returns None if the user has no organizer role or if the user account is blocked.
        Implementations must return None when the user has ``ban_status.is_blocked = True``.
        """
        ...

    async def is_unique(self, phone_number: str, contact_email: str) -> bool:
        """Check if organizer with given phone number or contact email already exists.

        Returns True if no organizer exists with these credentials.
        Returns False if organizer with phone_number or contact_email already exists.
        """
        ...

    async def is_unique_by_email(self, contact_email: str) -> bool:
        """Check if no organizer with the given contact email exists.

        Returns True if no organizer uses this email.
        """
        ...
