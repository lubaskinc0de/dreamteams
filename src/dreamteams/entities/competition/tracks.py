from collections.abc import Iterable

from dreamteams.entities.competition.track import CompetitionTrack
from dreamteams.entities.errors.competition import InvalidCompetitionDataError

_NO_ITEMS = object()


class CompetitionTracks(list[CompetitionTrack]):
    """Validated collection of competition tracks."""

    def __init__(self, items: Iterable[CompetitionTrack] | object = _NO_ITEMS) -> None:
        if items is _NO_ITEMS:
            # Collection instrumentation creates an empty container first; explicit empty domain data is rejected below.
            super().__init__()
            return

        if not isinstance(items, Iterable):
            msg = "CompetitionTracks items must be iterable"
            raise TypeError(msg)

        super().__init__(items)
        if not self:
            raise InvalidCompetitionDataError(message="Competition tracks must not be empty")

        names = [track.name.casefold() for track in self]
        if len(names) != len(set(names)):
            raise InvalidCompetitionDataError(message="Competition track names must be unique")
