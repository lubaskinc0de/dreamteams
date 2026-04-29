from dataclasses import dataclass
from enum import Enum


class SkillLevel(Enum):
    """Skill proficiency level."""

    BEGINNER = "BEGINNER"
    INTERMEDIATE = "INTERMEDIATE"
    ADVANCED = "ADVANCED"
    EXPERT = "EXPERT"


@dataclass
class ParticipantSkill:
    """Participant skill with name and proficiency level."""

    name: str
    level: SkillLevel
