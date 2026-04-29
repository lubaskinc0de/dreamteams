from pydantic import BaseModel, Field


class ParticipantContactForm(BaseModel):
    """Form for creating a participant contact."""

    title: str = Field(min_length=1, max_length=70)
    value: str
