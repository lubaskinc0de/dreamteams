from dataclasses import dataclass

from dreamteams.entities.errors.competition import InvalidCompetitionDataError


@dataclass(frozen=True, slots=True)
class ParticipantLimits:
    """Participant limits with a maximum value."""

    max: int

    def __post_init__(self) -> None:
        """Validate participant limits."""
        if self.max <= 0:
            raise InvalidCompetitionDataError(message="Max participants must be greater than 0")
