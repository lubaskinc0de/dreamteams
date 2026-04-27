import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from dreamteams.entities.common.clock import Clock
from dreamteams.entities.competition.entity import Competition, UpdateCompetitionData
from dreamteams.entities.competition.schedule import CompetitionSchedule, ScheduleData
from dreamteams.entities.competition.team_size_range import TeamSizeRange
from dreamteams.entities.competition.vo.milestones import CompetitionMilestones
from dreamteams.entities.errors.base import AccessDeniedError
from dreamteams.entities.errors.competition import InvalidCompetitionDataError
from tests.unit.composite import (
    positive_ordered_pairs,
    valid_competition,
    valid_competition_update_data,
    valid_schedule_data,
    valid_schedule_data_no_team_formation,
)
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
        tags=valid_competition_update_data.tags,
        tracks=valid_competition_update_data.tracks,
        participant_type=valid_competition_update_data.participant_type,
        venue=valid_competition_update_data.venue,
        team_size=valid_competition_update_data.team_size,
        banner=None,
        auto_accept=valid_competition_update_data.auto_accept,
        is_archived=valid_competition_update_data.is_archived,
        milestones=valid_competition_update_data.milestones
        if valid_competition_update_data.milestones is not None
        else CompetitionMilestones(),
        created_at=competition.created_at,
        updated_at=competition.updated_at,
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
@given(
    st.data(),
    valid_competition_update_data(),
    valid_schedule_data_no_team_formation(),
    positive_ordered_pairs(),
)
def test_update_with_team_size_but_no_team_formation_dates_is_rejected(
    gateway: Gateway,
    clock: Clock,
    data: st.DataObject,
    valid_competition_update_data: UpdateCompetitionData,
    schedule: ScheduleData,
    team_range: tuple[int, int],
) -> None:
    """Updating to team_size set with no team_formation_* dates violates the pairing invariant."""
    # Arrange
    organizer = gateway.organizer.create()
    competition = data.draw(valid_competition(organizer, clock))
    min_team, max_team = team_range
    valid_competition_update_data.team_size = TeamSizeRange(min=min_team, max=max_team)
    valid_competition_update_data.schedule = schedule

    # Act / Assert
    with pytest.raises(
        InvalidCompetitionDataError,
        match=r"team_size and schedule\.team_formation_\* must be set together",
    ):
        competition.update(valid_competition_update_data, organizer, clock)


@settings(max_examples=30)
@given(st.data(), valid_competition_update_data(), valid_schedule_data())
def test_update_with_team_formation_dates_but_no_team_size_is_rejected(
    gateway: Gateway,
    clock: Clock,
    data: st.DataObject,
    valid_competition_update_data: UpdateCompetitionData,
    schedule: ScheduleData,
) -> None:
    """Updating to team_formation_* dates set with no team_size violates the pairing invariant."""
    # Arrange
    organizer = gateway.organizer.create()
    competition = data.draw(valid_competition(organizer, clock))
    valid_competition_update_data.team_size = None
    valid_competition_update_data.schedule = schedule

    # Act / Assert
    with pytest.raises(
        InvalidCompetitionDataError,
        match=r"team_size and schedule\.team_formation_\* must be set together",
    ):
        competition.update(valid_competition_update_data, organizer, clock)
