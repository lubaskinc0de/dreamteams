import secrets

from polyfactory.factories import DataclassFactory

from dreamteams.entities.organizer_invite import OrganizerInvite
from dreamteams.entities.user import Organizer


def _code() -> str:
    return secrets.token_urlsafe(32)


class OrganizerInviteFactory(DataclassFactory[OrganizerInvite]):
    """Factory of OrganizerInvite entities."""

    __model__ = OrganizerInvite

    code = _code
    is_revoked = False
    is_used = False
    used_by: Organizer | None = None
