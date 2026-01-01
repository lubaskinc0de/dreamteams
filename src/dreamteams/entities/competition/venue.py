from dataclasses import dataclass
from enum import StrEnum, auto

from dreamteams.entities.errors.competition import InvalidCompetitionDataError


class CompetitionFormat(StrEnum):
    """Format in which a competition is conducted."""

    ONLINE = auto()
    OFFLINE = auto()
    HYBRID = auto()


@dataclass(frozen=True, slots=True)
class CompetitionVenue:
    """Competition venue with format and location."""

    format: CompetitionFormat
    location: str | None

    def __post_init__(self) -> None:
        """Validate that location is provided for offline or hybrid formats."""
        if self.format in (CompetitionFormat.OFFLINE, CompetitionFormat.HYBRID) and (
            self.location is None or not self.location.strip()
        ):
            raise InvalidCompetitionDataError(message="Location is required for offline or hybrid format")
