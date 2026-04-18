"""Gateway for OrganizerInvite entity construction in unit tests."""

from dataclasses import dataclass
from uuid import uuid4

from dreamteams.entities.organizer_invite import OrganizerInvite, organizer_invite_factory
from dreamteams.entities.user import User
from tests.unit.helpers.user_gateway import UserGateway


@dataclass
class OrganizerInviteGateway:
    """Gateway for issuing OrganizerInvite entities via the domain factory."""

    user_gateway: UserGateway

    def create(
        self,
        *,
        creator: User | None = None,
        display_name: str | None = None,
    ) -> OrganizerInvite:
        """Issue an invite as an admin (creating a fresh admin if none given)."""
        admin = creator if creator is not None else self.user_gateway.create_admin()

        return organizer_invite_factory(invite_id=uuid4(), display_name=display_name, user=admin)
