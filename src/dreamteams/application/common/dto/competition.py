from datetime import datetime

from pydantic import BaseModel

from dreamteams.entities.common.identifiers import CompetitionId, OrganizerId
from dreamteams.entities.common.participant_type import ParticipantType
from dreamteams.entities.competition.entity import Banner
from dreamteams.entities.competition.milestone import Milestone
from dreamteams.entities.competition.participant_limits import ParticipantLimits
from dreamteams.entities.competition.schedule import CompetitionSchedule
from dreamteams.entities.competition.tag import CompetitionTag
from dreamteams.entities.competition.team_size_range import TeamSizeRange
from dreamteams.entities.competition.track import CompetitionTrack
from dreamteams.entities.competition.venue import CompetitionVenue


class CompetitionModel(BaseModel):
    """Read model for an organizer's own competition."""

    id: CompetitionId
    organizer_id: OrganizerId
    title: str
    banner: Banner | None
    description: str
    schedule: CompetitionSchedule
    participant_limits: ParticipantLimits
    tags: list[CompetitionTag]
    tracks: list[CompetitionTrack]
    participant_type: ParticipantType
    venue: CompetitionVenue
    team_size: TeamSizeRange | None
    milestones: list[Milestone]
    auto_accept: bool
    is_archived: bool
    members_count: int
    created_at: datetime
    updated_at: datetime
