from dataclasses import dataclass

from dreamteams.entities.errors.participant import InvalidParticipantContactError


@dataclass(frozen=True)
class ParticipantContact:
    """Participant contact link with title validation."""

    title: str
    url: str

    def __post_init__(self) -> None:
        """Validate title."""
        if not self.title:
            raise InvalidParticipantContactError(message="Contact title not must be empty")
