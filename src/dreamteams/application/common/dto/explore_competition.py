from datetime import datetime

from pydantic import BaseModel

from dreamteams.entities.common.identifiers import CompetitionId, OrganizerId
from dreamteams.entities.common.vo.domain import Domain
from dreamteams.entities.common.vo.participant_type import ParticipantType
from dreamteams.entities.competition.entity import Banner
from dreamteams.entities.competition.milestone import Milestone
from dreamteams.entities.competition.participant_limits import ParticipantLimits
from dreamteams.entities.competition.schedule import CompetitionSchedule
from dreamteams.entities.competition.team_size_range import TeamSizeRange
from dreamteams.entities.competition.venue import CompetitionVenue


class ExploreOrganizerModel(BaseModel):
    """Organizer summary shown on the participant-facing explore list."""

    id: OrganizerId
    name: str
    avatar_url: str | None


class ExploreCompetitionModel(BaseModel):
    """Read model for the participant-facing explore list."""

    id: CompetitionId
    organizer: ExploreOrganizerModel
    title: str
    banner: Banner | None
    description: str
    schedule: CompetitionSchedule
    participant_limits: ParticipantLimits
    domains: list[Domain]
    participant_type: ParticipantType
    venue: CompetitionVenue
    team_size: TeamSizeRange
    milestones: list[Milestone]
    auto_accept: bool
    members_count: int
    created_at: datetime
    updated_at: datetime
