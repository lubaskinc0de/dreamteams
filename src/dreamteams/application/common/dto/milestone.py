from datetime import datetime

from pydantic import BaseModel, Field


class MilestoneForm(BaseModel):
    """Form for creating a milestone."""

    title: str = Field(min_length=1, max_length=50)
    timestamp: datetime
    description: str | None = Field(default=None, max_length=300)
