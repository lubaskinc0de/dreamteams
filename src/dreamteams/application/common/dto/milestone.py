from datetime import datetime

from pydantic import BaseModel, Field

from dreamteams.entities.competition.milestone_description import MilestoneDescription


class MilestoneForm(BaseModel):
    """Form for creating a milestone."""

    title: str = Field(max_length=50)
    timestamp: datetime
    description: str | None = Field(default=None, max_length=MilestoneDescription.MAX_LENGTH)
