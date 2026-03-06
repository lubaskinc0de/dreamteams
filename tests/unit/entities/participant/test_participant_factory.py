from hypothesis import HealthCheck, given, settings

from dreamteams.entities.common.clock import Clock
from dreamteams.entities.participant.entity import (
    Participant,
    ParticipantData,
    participant_factory,
)
from dreamteams.entities.user import User
from tests.unit.composite import valid_participant_data


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(valid_participant_data())
def test_create_participant_with_valid_data(
    user_without_organizer: User,
    clock: Clock,
    data: ParticipantData,
) -> None:
    """Test creating competition succeeds."""
    participant = participant_factory(data=data, user=user_without_organizer, clock=clock)

    assert participant == Participant(
        id=participant.id,
        user_id=participant.user_id,
        full_name=data.full_name,
        avatar_url=data.avatar_url,
        bio=data.bio,
        skills=data.skills,
        experience_level=data.experience_level,
        preferred_domains=data.preferred_domains,
        contacts=participant.contacts,
        created_at=participant.created_at,
        updated_at=participant.updated_at,
    )
