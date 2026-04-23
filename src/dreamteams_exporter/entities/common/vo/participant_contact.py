from dataclasses import dataclass


@dataclass(slots=True, kw_only=True, frozen=True)
class ParticipantContact:
    """Participant contact link."""

    title: str
    url: str
