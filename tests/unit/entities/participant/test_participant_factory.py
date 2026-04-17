import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from dreamteams.entities.common.clock import Clock
from dreamteams.entities.errors.participant import InvalidParticipantDataError
from dreamteams.entities.participant.vo.age import Age
from dreamteams.entities.participant.vo.participant_contact import ParticipantContact
from dreamteams.entities.user import (
    Participant,
    ParticipantData,
    User,
    participant_factory,
)
from tests.unit.composite import participant_contact_data, participant_skill_data, valid_participant_data


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow], max_examples=30)
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
        bio=data.bio,
        skills=data.skills,
        experience_level=data.experience_level,
        preferred_domains=data.preferred_domains,
        contacts=participant.contacts,
        participant_type=data.participant_type,
        age=data.age,
        created_at=participant.created_at,
        updated_at=participant.updated_at,
    )


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow], max_examples=10)
@given(valid_participant_data(), st.data())
def test_participant_skill_names_are_unique(
    user_without_organizer: User,
    clock: Clock,
    participant_data: ParticipantData,
    data: st.DataObject,
) -> None:
    """Test cannot create participant with duplicate skill names."""
    duplicate_skill = data.draw(participant_skill_data())
    participant_data.skills = [duplicate_skill] * 2

    with pytest.raises(InvalidParticipantDataError, match="Skill names must be unique"):
        participant_factory(
            data=participant_data,
            user=user_without_organizer,
            clock=clock,
        )


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow], max_examples=10)
@given(valid_participant_data(), st.data())
def test_participant_contact_titles_are_unique(
    user_without_organizer: User,
    clock: Clock,
    participant_data: ParticipantData,
    data: st.DataObject,
) -> None:
    """Test cannot create participant with duplicate contact titles."""
    contact = data.draw(participant_contact_data())
    participant_data.contacts = [contact, ParticipantContact(title=contact.title, url="https://other.example.com")]

    with pytest.raises(InvalidParticipantDataError, match="Contact titles must be unique"):
        participant_factory(
            data=participant_data,
            user=user_without_organizer,
            clock=clock,
        )


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow], max_examples=10)
@given(valid_participant_data(), st.data())
def test_participant_contact_urls_are_unique(
    user_without_organizer: User,
    clock: Clock,
    participant_data: ParticipantData,
    data: st.DataObject,
) -> None:
    """Test cannot create participant with duplicate contact URLs."""
    contact = data.draw(participant_contact_data())
    participant_data.contacts = [contact, ParticipantContact(title="Other Title", url=contact.url)]

    with pytest.raises(InvalidParticipantDataError, match="Contact URLs must be unique"):
        participant_factory(
            data=participant_data,
            user=user_without_organizer,
            clock=clock,
        )


@pytest.mark.parametrize("empty_string", ["", " ", "   "])
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow], max_examples=10)
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


@settings(suppress_health_check=[HealthCheck.too_slow], max_examples=10)
@given(st.integers(max_value=-1))
def test_participant_age_negative_is_invalid(age: int) -> None:
    """Test cannot create Age VO with negative value."""
    with pytest.raises(InvalidParticipantDataError, match="Age must be between 0 and 150"):
        Age(age)


@settings(suppress_health_check=[HealthCheck.too_slow], max_examples=10)
@given(st.integers(min_value=151))
def test_participant_age_above_maximum_is_invalid(age: int) -> None:
    """Test cannot create Age VO with value above maximum."""
    with pytest.raises(InvalidParticipantDataError, match="Age must be between 0 and 150"):
        Age(age)


@settings(suppress_health_check=[HealthCheck.too_slow], max_examples=10)
@given(st.integers(min_value=0, max_value=150))
def test_participant_age_valid(age: int) -> None:
    """Test Age VO accepts values in 0-150 range."""
    assert Age(age).value == age
