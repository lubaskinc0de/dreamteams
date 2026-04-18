from polyfactory.factories.pydantic_factory import ModelFactory

from dreamteams.application.manage_profile.update_organizer import UpdateOrganizerForm
from dreamteams.presentation.fast_api.routers.organizers import OrganizerForm
from tests.common.factory.providers import generate_ru_phone_number


def _generate_organizer_phone_number() -> str:
    """Generate fake organizer phone number."""
    return generate_ru_phone_number(OrganizerFormFactory.__faker__)


class OrganizerFormFactory(ModelFactory[OrganizerForm]):
    """Factory of OrganizerForm models."""

    __model__ = OrganizerForm
    phone_number = _generate_organizer_phone_number


class UpdateOrganizerFormFactory(ModelFactory[UpdateOrganizerForm]):
    """Factory of UpdateOrganizerForm models."""

    __model__ = UpdateOrganizerForm
