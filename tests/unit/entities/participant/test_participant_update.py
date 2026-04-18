import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from dreamteams.entities.common.clock import Clock
from dreamteams.entities.errors.participant import InvalidParticipantDataError
from dreamteams.entities.participant.vo.age import Age
from dreamteams.entities.participant.vo.participant_contact import ParticipantContact
from dreamteams.entities.user import Participant, UpdateParticipantData
from tests.unit.composite import (
    participant_contact_data,
    participant_skill_data,
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
        preferred_domains=valid_participant_update_data.preferred_domains,
        contacts=valid_participant_update_data.contacts,
        participant_type=valid_participant_update_data.participant_type,
        age=valid_participant_update_data.age,
        created_at=participant.created_at,
        updated_at=participant.updated_at,
    )


@settings(max_examples=10)
@given(st.data(), valid_participant_update_data())
def test_participant_skill_names_are_unique(
    gateway: Gateway,
    clock: Clock,
    data: st.DataObject,
    valid_participant_update_data: UpdateParticipantData,
) -> None:
    """Test cannot update participant with duplicate skill names."""
    user = gateway.user.create()
    participant = data.draw(valid_participant(user=user, clock=clock))
    duplicate_skill = data.draw(participant_skill_data())
    valid_participant_update_data.skills = [duplicate_skill] * 2

    with pytest.raises(InvalidParticipantDataError, match="Skill names must be unique"):
        participant.update(
            data=valid_participant_update_data,
            clock=clock,
        )


@settings(max_examples=10)
@given(st.data(), valid_participant_update_data())
def test_participant_contact_titles_are_unique(
    gateway: Gateway,
    clock: Clock,
    data: st.DataObject,
    valid_participant_update_data: UpdateParticipantData,
) -> None:
    """Test cannot update participant with duplicate contact titles."""
    user = gateway.user.create()
    participant = data.draw(valid_participant(user=user, clock=clock))
    contact = data.draw(participant_contact_data())
    valid_participant_update_data.contacts = [
        contact,
        ParticipantContact(title=contact.title, url="https://other.example.com"),
    ]

    with pytest.raises(InvalidParticipantDataError, match="Contact titles must be unique"):
        participant.update(
            data=valid_participant_update_data,
            clock=clock,
        )


@settings(max_examples=10)
@given(st.data(), valid_participant_update_data())
def test_participant_contact_urls_are_unique(
    gateway: Gateway,
    clock: Clock,
    data: st.DataObject,
    valid_participant_update_data: UpdateParticipantData,
) -> None:
    """Test cannot update participant with duplicate contact URLs."""
    user = gateway.user.create()
    participant = data.draw(valid_participant(user=user, clock=clock))
    contact = data.draw(participant_contact_data())
    valid_participant_update_data.contacts = [contact, ParticipantContact(title="Other Title", url=contact.url)]

    with pytest.raises(InvalidParticipantDataError, match="Contact URLs must be unique"):
        participant.update(
            data=valid_participant_update_data,
            clock=clock,
        )


@pytest.mark.parametrize("empty_string", ["", " ", "   "])
@settings(max_examples=10)
@given(st.data(), valid_participant_update_data())
def test_participant_full_name_is_not_empty(
    empty_string: str,
    gateway: Gateway,
    clock: Clock,
    data: st.DataObject,
    valid_participant_update_data: UpdateParticipantData,
) -> None:
    """Test cannot update participant with empty full name."""
    user = gateway.user.create()
    participant = data.draw(valid_participant(user=user, clock=clock))
    valid_participant_update_data.full_name = empty_string

    with pytest.raises(InvalidParticipantDataError, match="Full name must not be empty"):
        participant.update(
            data=valid_participant_update_data,
            clock=clock,
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
