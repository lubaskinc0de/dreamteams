from dataclasses import dataclass

from dreamteams.entities.errors.competition import InvalidCompetitionDataError


@dataclass(frozen=True, slots=True)
class ParticipantLimits:
    """Participant limits with minimum and maximum values."""

    max: int
    min: int

    def __post_init__(self) -> None:
        """Validate participant limits."""
        if self.max <= 0:
            raise InvalidCompetitionDataError(message="Max participants must be greater than 0")

        if self.min <= 0:
            raise InvalidCompetitionDataError(message="Min participants must be greater than 0")

        if self.min > self.max:
            raise InvalidCompetitionDataError(message="Min participants must be less than or equal to max participants")
