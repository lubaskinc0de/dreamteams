from polyfactory.factories.pydantic_factory import ModelFactory

from dreamteams.application.common.dto.competition_track import CompetitionTrackForm
from dreamteams.application.submit_application import SubmitApplicationInput


def _track_provider() -> CompetitionTrackForm:
    """Generate a track for an application."""
    return CompetitionTrackForm(name="General")


class SubmitApplicationInputFactory(ModelFactory[SubmitApplicationInput]):
    """Factory for SubmitApplicationInput models.

    Generates a default track. Set ``form_data`` explicitly when the competition
    has an ApplicationForm attached.
    """

    __model__ = SubmitApplicationInput

    track = _track_provider
