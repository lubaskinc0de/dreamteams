from hypothesis import given, settings
from hypothesis import strategies as st

from dreamteams.entities.common.clock import Clock
from dreamteams.entities.participant.vo.age import Age
from dreamteams.entities.user import Participant, UpdateParticipantData
from tests.unit.composite import (
    valid_participant,
    valid_participant_update_data,
)
from tests.unit.helpers.facade import Gateway


@settings(max_examples=30)
@given(st.data(), valid_participant_update_data())
def test_update_participant_succeeds(
    gateway: Gateway,
    clock: Clock,
    data: st.DataObject,
    valid_participant_update_data: UpdateParticipantData,
) -> None:
    """Test updating participant succeeds."""
    user = gateway.user.create()
    participant = data.draw(valid_participant(user=user, clock=clock))

    participant.update(
        data=valid_participant_update_data,
        clock=clock,
    )

    assert participant == Participant(
        id=participant.id,
        user_id=user.id,
        full_name=valid_participant_update_data.full_name,
        bio=valid_participant_update_data.bio,
        skills=valid_participant_update_data.skills,
        experience_level=valid_participant_update_data.experience_level,
        contacts=valid_participant_update_data.contacts,
        participant_type=valid_participant_update_data.participant_type,
        age=valid_participant_update_data.age,
        created_at=participant.created_at,
        updated_at=participant.updated_at,
    )


@settings(max_examples=10)
@given(st.data(), valid_participant_update_data(), st.integers(min_value=0, max_value=150))
def test_update_participant_age(
    gateway: Gateway,
    clock: Clock,
    data: st.DataObject,
    valid_participant_update_data: UpdateParticipantData,
    valid_age: int,
) -> None:
    """Test updating participant age succeeds."""
    user = gateway.user.create()
    participant = data.draw(valid_participant(user=user, clock=clock))
    valid_participant_update_data.age = Age(valid_age)

    participant.update(data=valid_participant_update_data, clock=clock)

    assert participant.age == Age(valid_age)
