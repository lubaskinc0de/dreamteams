from dataclasses import dataclass

from dreamteams_exporter.entities.common.identifiers import ParticipantId
from dreamteams_exporter.entities.common.vo.participant_contact import ParticipantContact


@dataclass(slots=True, kw_only=True)
class Participant:
    """Participant profile as exported alongside each application row."""

    id: ParticipantId
    full_name: str
    bio: str | None
    participant_type: str
    age: int
    contacts: list[ParticipantContact]
