from polyfactory.factories.pydantic_factory import ModelFactory

from dreamteams.application.manage_profile.update_organizer import UpdateOrganizerForm
from dreamteams.presentation.fast_api.routers.organizers import OrganizerForm


def _generate_organizer_phone_number() -> str:
    """Generate fake organizer phone number."""
    faker = OrganizerFormFactory.__faker__
    return "+79" + faker.numerify("#########")


class OrganizerFormFactory(ModelFactory[OrganizerForm]):
    """Factory of OrganizerForm models."""

    __model__ = OrganizerForm
    phone_number = _generate_organizer_phone_number


class UpdateOrganizerFormFactory(ModelFactory[UpdateOrganizerForm]):
    """Factory of UpdateOrganizerForm models."""

    __model__ = UpdateOrganizerForm
