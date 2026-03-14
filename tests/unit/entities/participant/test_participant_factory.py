import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from dreamteams.entities.common.clock import Clock
from dreamteams.entities.errors.participant import InvalidParticipantDataError
from dreamteams.entities.participant.entity import (
    Participant,
    ParticipantData,
    participant_factory,
)
from dreamteams.entities.user import User
from tests.unit.composite import participant_contact_data, valid_participant_data


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=30)
@given(valid_participant_data())
def test_create_participant_with_valid_data(
    user_without_organizer: User,
    clock: Clock,
    data: ParticipantData,
) -> None:
    """Test creating participant succeeds."""
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


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=10)
@given(valid_participant_data(), st.data())
def test_participant_contacts_are_unique(
    user_without_organizer: User,
    clock: Clock,
    participant_data: ParticipantData,
    data: st.DataObject,
) -> None:
    """Test cannot create participant with duplicate contacts."""
    participant_data.contacts = [data.draw(participant_contact_data())] * 2

    with pytest.raises(InvalidParticipantDataError, match="Contact URLs must be unique"):
        participant_factory(
            data=participant_data,
            user=user_without_organizer,
            clock=clock,
        )


@pytest.mark.parametrize("empty_string", ["", " ", "   "])
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=10)
@given(valid_participant_data())
def test_participant_full_name_is_not_empty(
    empty_string: str,
    user_without_organizer: User,
    clock: Clock,
    data: ParticipantData,
) -> None:
    """Test cannot create participant with empty full name."""
    data.full_name = empty_string

    with pytest.raises(InvalidParticipantDataError, match="Full name must not be empty"):
        participant_factory(
            data=data,
            user=user_without_organizer,
            clock=clock,
        )


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=10)
@given(valid_participant_data())
def test_participant_skills_are_not_empty(
    user_without_organizer: User,
    clock: Clock,
    data: ParticipantData,
) -> None:
    """Test cannot create participant with empty skills."""
    data.skills = []

    with pytest.raises(InvalidParticipantDataError, match="Skills list must not be empty"):
        participant_factory(
            data=data,
            user=user_without_organizer,
            clock=clock,
        )


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=10)
@given(valid_participant_data())
def test_participant_preferred_domains_are_not_empty(
    user_without_organizer: User,
    clock: Clock,
    data: ParticipantData,
) -> None:
    """Test cannot create participant with empty preferred domains."""
    data.preferred_domains = []

    with pytest.raises(InvalidParticipantDataError, match="Preferred domains list not be empty"):
        participant_factory(
            data=data,
            user=user_without_organizer,
            clock=clock,
        )
