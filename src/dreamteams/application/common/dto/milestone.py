from datetime import datetime

from pydantic import BaseModel, Field


class MilestoneForm(BaseModel):
    """Form for creating a milestone."""

    title: str = Field(max_length=50)
    timestamp: datetime
