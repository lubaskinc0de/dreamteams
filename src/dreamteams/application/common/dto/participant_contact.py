from pydantic import BaseModel, Field, HttpUrl


class ParticipantContactForm(BaseModel):
    """Form for creating a participant contact."""

    title: str = Field(min_length=1, max_length=70)
    url: HttpUrl
