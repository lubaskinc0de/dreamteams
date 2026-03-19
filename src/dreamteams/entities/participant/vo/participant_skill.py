from dataclasses import dataclass
from enum import Enum

from dreamteams.entities.errors.participant import InvalidParticipantDataError


class SkillLevel(Enum):
    """Skill proficiency level."""

    BEGINNER = "BEGINNER"
    INTERMEDIATE = "INTERMEDIATE"
    ADVANCED = "ADVANCED"
    EXPERT = "EXPERT"


@dataclass(frozen=True)
class ParticipantSkill:
    """Participant skill with name and proficiency level."""

    name: str
    level: SkillLevel

    def __post_init__(self) -> None:
        """Validate skill name."""
        if not self.name or self.name.isspace():
            raise InvalidParticipantDataError(message="Skill name must not be empty")
