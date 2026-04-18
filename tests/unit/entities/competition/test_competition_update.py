import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from dreamteams.entities.common.clock import Clock
from dreamteams.entities.competition.entity import Competition, UpdateCompetitionData
from dreamteams.entities.competition.schedule import CompetitionSchedule
from dreamteams.entities.errors.base import AccessDeniedError
from dreamteams.entities.errors.competition import InvalidCompetitionDataError
from tests.unit.composite import milestone, valid_competition, valid_competition_update_data
from tests.unit.helpers.facade import Gateway


@settings(max_examples=30)
@given(st.data(), valid_competition_update_data())
def test_update_competition_succeeds(
    gateway: Gateway,
    clock: Clock,
    data: st.DataObject,
    valid_competition_update_data: UpdateCompetitionData,
) -> None:
    """Test updating competition succeeds."""
    organizer = gateway.organizer.create()
    competition = data.draw(valid_competition(organizer, clock))

    competition.update(
        valid_competition_update_data,
        organizer,
        clock,
    )

    assert competition == Competition(
        id=competition.id,
        organizer_id=organizer.id,
        organizer=organizer,
        title=valid_competition_update_data.title,
        description=valid_competition_update_data.description,
        schedule=CompetitionSchedule(
            valid_competition_update_data.schedule.registration_start,
            valid_competition_update_data.schedule.registration_end,
            valid_competition_update_data.schedule.team_formation_start,
            valid_competition_update_data.schedule.team_formation_end,
        ),
        participant_limits=valid_competition_update_data.participant_limits,
        domains=valid_competition_update_data.domains,
        participant_type=valid_competition_update_data.participant_type,
        venue=valid_competition_update_data.venue,
        team_size=valid_competition_update_data.team_size,
        banner=None,
        auto_accept=valid_competition_update_data.auto_accept,
        is_archived=valid_competition_update_data.is_archived,
        milestones=valid_competition_update_data.milestones
        if valid_competition_update_data.milestones is not None
        else [],
        created_at=competition.created_at,
        updated_at=competition.updated_at,
    )


@settings(max_examples=30)
@given(st.data(), valid_competition_update_data())
def test_competition_milestones_are_unique(
    gateway: Gateway,
    clock: Clock,
    data: st.DataObject,
    valid_competition_update_data: UpdateCompetitionData,
) -> None:
    """Test cannot create competition with duplicate milestones."""
    organizer = gateway.organizer.create()
    competition = data.draw(valid_competition(organizer, clock))
    valid_competition_update_data.milestones = [data.draw(milestone())] * 2

    with pytest.raises(InvalidCompetitionDataError, match="Milestone timestamps must be unique"):
        competition.update(
            valid_competition_update_data,
            organizer,
            clock,
        )


@settings(max_examples=30)
@given(st.data(), valid_competition_update_data())
def test_only_owner_can_update_competition(
    gateway: Gateway,
    clock: Clock,
    data: st.DataObject,
    valid_competition_update_data: UpdateCompetitionData,
) -> None:
    """Test only owner of this competition can update it."""
    organizer = gateway.organizer.create()
    different_organizer = gateway.organizer.create()
    competition = data.draw(valid_competition(organizer, clock))

    with pytest.raises(AccessDeniedError):
        competition.update(
            valid_competition_update_data,
            different_organizer,
            clock,
        )


@settings(max_examples=30)
@given(st.data(), valid_competition_update_data())
def test_competition_domains_are_not_empty(
    gateway: Gateway,
    clock: Clock,
    data: st.DataObject,
    valid_competition_update_data: UpdateCompetitionData,
) -> None:
    """Test cannot update competition with empty domains."""
    organizer = gateway.organizer.create()
    competition = data.draw(valid_competition(organizer, clock))
    valid_competition_update_data.domains = []

    with pytest.raises(InvalidCompetitionDataError, match="Domains list must not be empty"):
        competition.update(
            valid_competition_update_data,
            organizer,
            clock,
        )


@pytest.mark.parametrize("empty_string", ["", " ", "   "])
@settings(max_examples=30)
@given(st.data(), valid_competition_update_data())
def test_competition_descriptions_are_not_empty(
    empty_string: str,
    gateway: Gateway,
    clock: Clock,
    data: st.DataObject,
    valid_competition_update_data: UpdateCompetitionData,
) -> None:
    """Test cannot update competition with empty description."""
    organizer = gateway.organizer.create()
    competition = data.draw(valid_competition(organizer, clock))
    valid_competition_update_data.description = empty_string

    with pytest.raises(InvalidCompetitionDataError, match="Description must not be empty"):
        competition.update(
            valid_competition_update_data,
            organizer,
            clock,
        )
