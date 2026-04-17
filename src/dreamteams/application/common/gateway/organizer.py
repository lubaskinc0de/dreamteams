from typing import Protocol


class OrganizerGateway(Protocol):
    """Gateway for checking organizer uniqueness."""

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
