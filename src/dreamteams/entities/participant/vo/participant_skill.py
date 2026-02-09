from dataclasses import dataclass
from enum import Enum


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
        cleaned = self.name.strip()
        if not cleaned:
            error_message = "Skill name must not be empty"
            raise ValueError(error_message)

        object.__setattr__(self, "name", cleaned)
