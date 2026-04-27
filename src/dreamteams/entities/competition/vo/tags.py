from collections.abc import Iterable

from dreamteams.entities.competition.tag import CompetitionTag
from dreamteams.entities.errors.competition import InvalidCompetitionDataError


class CompetitionTags(list[CompetitionTag]):
    """Validated collection of competition tags."""

    def __init__(self, items: Iterable[CompetitionTag] = ()) -> None:
        super().__init__(items)
        ids = [tag.id for tag in self]
        if len(ids) != len(set(ids)):
            raise InvalidCompetitionDataError(message="Competition tags must be unique")

        values = [tag.value.casefold() for tag in self]
        if len(values) != len(set(values)):
            raise InvalidCompetitionDataError(message="Competition tags must be unique")
