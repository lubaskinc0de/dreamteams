"""Gateway for Organizer entity construction in unit tests."""

from dataclasses import dataclass

from dreamteams.entities.user import Organizer, User
from tests.common.factory.entities.organizer import OrganizerFactory
from tests.unit.helpers.user_gateway import UserGateway


@dataclass
class OrganizerGateway:
    """Gateway for building Organizer entities and wiring them to Users."""

    organizer_factory: type[OrganizerFactory]
    user_gateway: UserGateway

    def create(self, user: User | None = None) -> Organizer:
        """Build an Organizer attached to a fresh or provided User (linked via ``make_organizer``)."""
        u = user if user is not None else self.user_gateway.create()

        organizer = self.organizer_factory.build(user=u, user_id=u.id)
        u.make_organizer(organizer)

        return organizer
