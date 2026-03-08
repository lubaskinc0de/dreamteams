import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from dreamteams.entities.common.clock import Clock
from dreamteams.entities.errors.participant import InvalidParticipantDataError
from dreamteams.entities.participant.entity import Participant, UpdateParticipantData
from dreamteams.entities.user import User
from tests.unit.composite import valid_participant, valid_participant_update_data


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(st.data(), valid_participant_update_data())
def test_update_participant_succeeds(
    user_without_organizer: User,
    clock: Clock,
    data: st.DataObject,
    valid_participant_update_data: UpdateParticipantData,
) -> None:
    """Test updating participant succeeds."""
    participant = data.draw(valid_participant(user=user_without_organizer, clock=clock))

    participant.update(
        data=valid_participant_update_data,
        clock=clock,
    )

    assert participant == Participant(
        id=participant.id,
        user_id=user_without_organizer.id,
        full_name=valid_participant_update_data.full_name,
        avatar_url=valid_participant_update_data.avatar_url,
        bio=valid_participant_update_data.bio,
        skills=valid_participant_update_data.skills,
        experience_level=valid_participant_update_data.experience_level,
        preferred_domains=valid_participant_update_data.preferred_domains,
        contacts=valid_participant_update_data.contacts,
        created_at=participant.created_at,
        updated_at=participant.update_at,
    )



