from dataclasses import dataclass

from dreamteams.entities.errors.competition import InvalidCompetitionDataError


@dataclass(frozen=True, slots=True)
class TeamSizeRange:
    """Team size range with minimum and maximum values."""

    max: int
    min: int

    def __post_init__(self) -> None:
        """Validate team size range."""
        if self.min < 1:
            raise InvalidCompetitionDataError(message="Min team size must be at least 1")

        if self.max <= 0:
            raise InvalidCompetitionDataError(message="Max team size must be greater than 0")

        if self.min > self.max:
            raise InvalidCompetitionDataError(message="Min team size must be less than or equal to max team size")
