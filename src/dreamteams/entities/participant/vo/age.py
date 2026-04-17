from dataclasses import dataclass

from dreamteams.entities.errors.participant import InvalidParticipantDataError

AGE_MIN = 0
AGE_MAX = 150


@dataclass
class Age:
    """Participant age value object."""

    value: int

    def __post_init__(self) -> None:
        """Validate age is within allowed bounds."""
        if not (AGE_MIN <= self.value <= AGE_MAX):
            raise InvalidParticipantDataError(message="Age must be between 0 and 150")
