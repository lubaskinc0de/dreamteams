import secrets
from dataclasses import dataclass, field
from datetime import UTC, datetime

from dreamteams.entities.base import Entity
from dreamteams.entities.common.identifiers import OrganizerInviteId, UserId
from dreamteams.entities.errors.base import AccessDeniedError
from dreamteams.entities.errors.invite import (
    InviteAlreadyRevokedError,
    InviteAlreadyUsedError,
    InviteRevokedError,
)
from dreamteams.entities.user import Organizer, User


@dataclass
class OrganizerInvite(Entity):
    """An invite code that permits one user to register as an organizer."""

    id: OrganizerInviteId
    code: str
    display_name: str | None
    created_by: UserId
    is_revoked: bool = False
    is_used: bool = False
    used_by: Organizer | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def revoke(self, user: User) -> None:
        """Revoke this invite on behalf of a user.

        Raises:
            AccessDeniedError: If the user is not an admin or not the creator.
            InviteAlreadyUsedError: If the invite has already been used.
            InviteAlreadyRevokedError: If the invite has already been revoked.

        """
        if not user.is_admin:
            raise AccessDeniedError(message="Only admins can revoke invites")
        if self.created_by != user.id:
            raise AccessDeniedError(message="You can only revoke invites you created")
        if self.is_used:
            raise InviteAlreadyUsedError
        if self.is_revoked:
            raise InviteAlreadyRevokedError
        self.is_revoked = True

    def ensure_can_read(self, user: User) -> None:
        """Assert that the user is allowed to read this invite.

        Raises:
            AccessDeniedError: If the user is not an admin or not the creator of the invite.

        """
        if not user.is_admin:
            raise AccessDeniedError(message="Only admins can read invites")
        if self.created_by != user.id:
            raise AccessDeniedError(message="You can only read invites you created")

    def use(self, organizer: Organizer) -> None:
        """Mark this invite as used during organizer registration.

        Raises:
            InviteRevokedError: If the invite has been revoked.
            InviteAlreadyUsedError: If the invite has already been used.

        """
        if self.is_revoked:
            raise InviteRevokedError
        if self.is_used:
            raise InviteAlreadyUsedError
        self.is_used = True
        self.used_by = organizer


def ensure_can_list_invites(user: User) -> None:
    """Assert that the user is allowed to list organizer invites.

    Raises:
        AccessDeniedError: If the user is not an admin.

    """
    if not user.is_admin:
        raise AccessDeniedError(message="Only admins can list invites")


def organizer_invite_factory(
    invite_id: OrganizerInviteId,
    display_name: str | None,
    user: User,
) -> OrganizerInvite:
    """Create a new ``OrganizerInvite`` entity. Only admin users can create invites."""
    if not user.is_admin:
        raise AccessDeniedError(message="Only admins can issue invites")
    code = secrets.token_urlsafe(32)
    return OrganizerInvite(
        id=invite_id,
        code=code,
        display_name=display_name,
        created_by=user.id,
    )
