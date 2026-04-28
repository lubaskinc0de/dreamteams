import pytest
from hypothesis import given, settings

from dreamteams.entities.competition.entity import Competition, CompetitionData, competition_factory
from dreamteams.entities.competition.milestone import milestone_factory
from dreamteams.entities.competition.milestones import CompetitionMilestones
from dreamteams.entities.competition.schedule import CompetitionSchedule, ScheduleData
from dreamteams.entities.competition.team_size_range import TeamSizeRange
from dreamteams.entities.errors.competition import InvalidCompetitionDataError
from dreamteams_common.clock import Clock
from tests.unit.composite import (
    positive_ordered_pairs,
    valid_competition_data,
    valid_schedule_data,
    valid_schedule_data_no_team_formation,
)
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
        tags=data.tags,
        tracks=data.tracks,
        participant_type=data.participant_type,
        venue=data.venue,
        team_size=data.team_size,
        banner=None,
        auto_accept=data.auto_accept,
        is_archived=True,
        milestones=CompetitionMilestones(
            [milestone_factory(milestone_data, clock) for milestone_data in data.milestones],
        )
        if data.milestones is not None
        else CompetitionMilestones(),
        created_at=competition.created_at,
        updated_at=competition.updated_at,
    )


@settings(max_examples=30)
@given(valid_competition_data(), valid_schedule_data_no_team_formation(), positive_ordered_pairs())
def test_team_size_without_team_formation_dates_is_rejected(
    gateway: Gateway,
    clock: Clock,
    data: CompetitionData,
    schedule: ScheduleData,
    team_range: tuple[int, int],
) -> None:
    """team_size set with no team_formation_* dates violates the pairing invariant."""
    # Arrange
    organizer = gateway.organizer.create()
    min_team, max_team = team_range
    data.team_size = TeamSizeRange(min=min_team, max=max_team)
    data.schedule = schedule

    # Act / Assert
    with pytest.raises(
        InvalidCompetitionDataError,
        match=r"team_size and schedule\.team_formation_\* must be set together",
    ):
        competition_factory(organizer=organizer, data=data, clock=clock)


@settings(max_examples=30)
@given(valid_competition_data(), valid_schedule_data())
def test_team_formation_dates_without_team_size_are_rejected(
    gateway: Gateway,
    clock: Clock,
    data: CompetitionData,
    schedule: ScheduleData,
) -> None:
    """team_formation_* dates set with no team_size violates the pairing invariant."""
    # Arrange
    organizer = gateway.organizer.create()
    data.team_size = None
    data.schedule = schedule

    # Act / Assert
    with pytest.raises(
        InvalidCompetitionDataError,
        match=r"team_size and schedule\.team_formation_\* must be set together",
    ):
        competition_factory(organizer=organizer, data=data, clock=clock)
