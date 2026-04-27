from collections.abc import Iterable

from dreamteams.entities.competition.milestone import Milestone
from dreamteams.entities.errors.competition import InvalidCompetitionDataError


class CompetitionMilestones(list[Milestone]):
    """Validated collection of competition milestones — timestamps must be unique."""

    def __init__(self, items: Iterable[Milestone] = ()) -> None:
        super().__init__(items)
        timestamps = [m.timestamp for m in self]
        if len(timestamps) != len(set(timestamps)):
            raise InvalidCompetitionDataError(message="Milestone timestamps must be unique")
