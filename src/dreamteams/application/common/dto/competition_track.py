from pydantic import BaseModel, Field


class CompetitionTrackForm(BaseModel):
    """Request model for a competition track."""

    name: str = Field(min_length=1, max_length=100)
