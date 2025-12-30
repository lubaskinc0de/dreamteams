from polyfactory.factories.pydantic_factory import ModelFactory

from dreamteams.presentation.fast_api.routers.organizers import OrganizerForm


class OrganizerFormFactory(ModelFactory[OrganizerForm]):
    """Factory of OrganizerForm models."""

    __model__ = OrganizerForm
