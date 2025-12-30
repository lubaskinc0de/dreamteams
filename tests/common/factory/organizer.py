from polyfactory.factories.pydantic_factory import ModelFactory

from dreamteams.presentation.fast_api.routers.organizers import OrganizerForm


def _generate_organizer_phone_number() -> str:
    """Generate fake organizer phone number."""
    faker = OrganizerFormFactory.__faker__
    return "+79" + faker.numerify("#########")


class OrganizerFormFactory(ModelFactory[OrganizerForm]):
    """Factory of OrganizerForm models."""

    __model__ = OrganizerForm
    phone_number = _generate_organizer_phone_number
