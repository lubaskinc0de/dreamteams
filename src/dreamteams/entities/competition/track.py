from dataclasses import dataclass

from dreamteams.entities.errors.competition import InvalidCompetitionDataError


@dataclass
class CompetitionTrack:
    """Competition direction/category selected by applicants."""

    name: str

    def __post_init__(self) -> None:
        """Normalize and validate track name."""
        self.name = self.name.strip()
        if not self.name:
            raise InvalidCompetitionDataError(message="Track name must not be empty")
