from dataclasses import dataclass
from typing import ClassVar

from dreamteams.entities.errors.competition import InvalidCompetitionDataError


@dataclass(frozen=True, slots=True)
class MilestoneDescription:
    """Free-form context for a competition milestone."""

    MAX_LENGTH: ClassVar[int] = 300

    value: str

    def __post_init__(self) -> None:
        """Validate length."""
        if len(self.value) > self.MAX_LENGTH:
            raise InvalidCompetitionDataError(
                message=f"Milestone description must be at most {self.MAX_LENGTH} characters",
            )
