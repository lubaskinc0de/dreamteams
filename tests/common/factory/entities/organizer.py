from polyfactory.decorators import post_generated
from polyfactory.factories import DataclassFactory

from dreamteams.entities.common.identifiers import UserId
from dreamteams.entities.user import Organizer, User
from tests.common.factory.entities.user import UserFactory
from tests.common.factory.providers import generate_ru_phone_number


def _user_provider() -> User:
    return UserFactory.build()


def _phone_provider() -> str:
    return generate_ru_phone_number(OrganizerFactory.__faker__)


class OrganizerFactory(DataclassFactory[Organizer]):
    """Factory of Organizer entities. ``user_id`` is always kept consistent with ``user.id``."""

    __model__ = Organizer

    user = _user_provider
    phone_number = _phone_provider

    @post_generated
    @classmethod
    def user_id(cls, user: User) -> UserId:
        """Keep ``user_id`` in sync with the generated ``user``."""
        return user.id
