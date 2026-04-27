import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from dreamteams.entities.common.clock import Clock
from dreamteams.entities.errors.participant import InvalidParticipantDataError
from dreamteams.entities.participant.vo.age import Age
from dreamteams.entities.user import (
    Participant,
    ParticipantData,
    participant_factory,
)
from tests.unit.composite import valid_participant_data
from tests.unit.helpers.facade import Gateway


@settings(max_examples=30)
@given(valid_participant_data())
def test_create_participant_with_valid_data(
    gateway: Gateway,
    clock: Clock,
    data: ParticipantData,
) -> None:
    """Test creating participant succeeds."""
    user = gateway.user.create()

    participant = participant_factory(data=data, user=user, clock=clock)

    assert participant == Participant(
        id=participant.id,
        user_id=participant.user_id,
        full_name=data.full_name,
        bio=data.bio,
        skills=data.skills,
        experience_level=data.experience_level,
        contacts=participant.contacts,
        participant_type=data.participant_type,
        age=data.age,
        created_at=participant.created_at,
        updated_at=participant.updated_at,
    )


@settings(max_examples=10)
@given(st.integers(max_value=-1))
def test_participant_age_negative_is_invalid(age: int) -> None:
    """Test cannot create Age VO with negative value."""
    with pytest.raises(InvalidParticipantDataError, match="Age must be between 0 and 150"):
        Age(age)


@settings(max_examples=10)
@given(st.integers(min_value=151))
def test_participant_age_above_maximum_is_invalid(age: int) -> None:
    """Test cannot create Age VO with value above maximum."""
    with pytest.raises(InvalidParticipantDataError, match="Age must be between 0 and 150"):
        Age(age)


@settings(max_examples=10)
@given(st.integers(min_value=0, max_value=150))
def test_participant_age_valid(age: int) -> None:
    """Test Age VO accepts values in 0-150 range."""
    assert Age(age).value == age
