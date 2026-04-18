import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from dreamteams.entities.common.clock import Clock
from dreamteams.entities.competition.entity import Competition, CompetitionData, competition_factory
from dreamteams.entities.competition.milestone import milestone_factory
from dreamteams.entities.competition.schedule import CompetitionSchedule
from dreamteams.entities.errors.competition import InvalidCompetitionDataError
from tests.unit.composite import milestone_data, valid_competition_data
from tests.unit.helpers.facade import Gateway


@settings(max_examples=30)
@given(valid_competition_data())
def test_create_competition_with_valid_data(
    gateway: Gateway,
    clock: Clock,
    data: CompetitionData,
) -> None:
    """Test creating competition succeeds."""
    organizer = gateway.organizer.create()

    competition = competition_factory(
        organizer=organizer,
        data=data,
        clock=clock,
    )

    assert competition.created_at == competition.updated_at
    assert competition == Competition(
        id=competition.id,
        organizer_id=organizer.id,
        organizer=organizer,
        title=data.title,
        description=data.description,
        schedule=CompetitionSchedule(
            data.schedule.registration_start,
            data.schedule.registration_end,
            data.schedule.team_formation_start,
            data.schedule.team_formation_end,
        ),
        participant_limits=data.participant_limits,
        domains=data.domains,
        participant_type=data.participant_type,
        venue=data.venue,
        team_size=data.team_size,
        banner=None,
        auto_accept=data.auto_accept,
        is_archived=True,
        milestones=[milestone_factory(milestone_data, clock) for milestone_data in data.milestones]
        if data.milestones is not None
        else [],
        created_at=competition.created_at,
        updated_at=competition.updated_at,
    )


@settings(max_examples=30)
@given(valid_competition_data(), st.data())
def test_competition_milestones_are_unique(
    gateway: Gateway,
    clock: Clock,
    competition_data: CompetitionData,
    data: st.DataObject,
) -> None:
    """Test cannot create competition with duplicate milestones."""
    organizer = gateway.organizer.create()
    competition_data.milestones = [data.draw(milestone_data())] * 2

    with pytest.raises(InvalidCompetitionDataError, match="Milestone timestamps must be unique"):
        competition_factory(
            organizer=organizer,
            data=competition_data,
            clock=clock,
        )


@settings(max_examples=30)
@given(valid_competition_data())
def test_competition_domains_list_is_not_empty(
    gateway: Gateway,
    clock: Clock,
    data: CompetitionData,
) -> None:
    """Test cannot create competition with empty domains list."""
    organizer = gateway.organizer.create()
    data.domains = []

    with pytest.raises(InvalidCompetitionDataError, match="Domains list must not be empty"):
        competition_factory(
            organizer=organizer,
            data=data,
            clock=clock,
        )


@pytest.mark.parametrize("empty_string", ["", " ", "   "])
@settings(max_examples=30)
@given(valid_competition_data())
def test_competition_description_is_not_empty(
    empty_string: str,
    gateway: Gateway,
    clock: Clock,
    data: CompetitionData,
) -> None:
    """Test cannot create competition with empty description."""
    organizer = gateway.organizer.create()
    data.description = empty_string

    with pytest.raises(InvalidCompetitionDataError, match="Description must not be empty"):
        competition_factory(
            organizer=organizer,
            data=data,
            clock=clock,
        )
