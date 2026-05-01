from pydantic import BaseModel, Field

MAX_CONTACT_VALUE_LENGTH = 500


class ParticipantContactForm(BaseModel):
    """Form for creating a participant contact."""

    title: str = Field(min_length=1, max_length=70)
    value: str = Field(min_length=1, max_length=MAX_CONTACT_VALUE_LENGTH)
