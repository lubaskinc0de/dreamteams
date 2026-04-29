from dataclasses import dataclass


@dataclass
class ParticipantContact:
    """Participant contact — title and any string value (URL, handle, phone, etc.)."""

    title: str
    value: str
