from dataclasses import dataclass
from enum import Enum

from dreamteams.entities.errors.participant import InvalidParticipantSkillError


class SkillLevel(Enum):
    """Skill proficiency level."""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


@dataclass(frozen=True)
class ParticipantSkill:
    """Participant skill with name and proficiency level."""

    name: str
    level: SkillLevel

    def __post_init__(self) -> None:
        """Validate skill name."""
        if not self.name:
            raise InvalidParticipantSkillError(message="Skill name must not be empty")
