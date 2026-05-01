from pydantic import BaseModel, Field

from dreamteams.entities.participant.participant_skill import SkillLevel

MAX_PARTICIPANT_SKILLS = 50


class ParticipantSkillForm(BaseModel):
    """Form for creating a participant skill."""

    name: str = Field(min_length=1, max_length=70)
    level: SkillLevel
