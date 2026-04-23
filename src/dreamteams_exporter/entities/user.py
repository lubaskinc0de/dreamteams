from dataclasses import dataclass

from dreamteams_exporter.entities.common.identifiers import (
    OrganizerId,
    ParticipantId,
    UserId,
)


@dataclass(slots=True, kw_only=True)
class User:
    """Local projection of a dreamteams user — only the fields the exporter cares about."""

    user_id: UserId
    organizer_id: OrganizerId | None
    participant_id: ParticipantId | None
