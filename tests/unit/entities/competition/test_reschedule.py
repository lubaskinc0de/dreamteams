from copy import deepcopy

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from dreamteams.entities.common.clock import Clock
from dreamteams.entities.competition.entity import Competition
from dreamteams.entities.competition.schedule import CompetitionSchedule, ScheduleData
from dreamteams.entities.competition.team_size_range import TeamSizeRange
from dreamteams.entities.errors.base import AccessDeniedError
from dreamteams.entities.errors.competition import InvalidCompetitionDataError
from tests.unit.composite import (
    positive_ordered_pairs,
    valid_competition,
    valid_schedule_data,
    valid_schedule_data_no_team_formation,
)
from tests.unit.helpers.facade import Gateway


@settings(max_examples=30)
@given(st.data(), valid_schedule_data(), positive_ordered_pairs())
def test_reschedule_succeeds(
    gateway: Gateway,
    clock: Clock,
    data: st.DataObject,
    schedule: ScheduleData,
    team_range: tuple[int, int],
) -> None:
    """Reschedule updates dates and team size while preserving general information."""
    # Arrange
    organizer = gateway.organizer.create()
    competition = data.draw(valid_competition(organizer, clock))
    min_team, max_team = team_range
    team_size = TeamSizeRange(min=min_team, max=max_team)
    before_update = deepcopy(competition)

    # Act
    competition.reschedule(schedule, team_size, organizer, clock)

    # Assert
    assert competition == Competition(
        id=competition.id,
        organizer_id=organizer.id,
        organizer=organizer,
        title=before_update.title,
        description=before_update.description,
        schedule=CompetitionSchedule(
            schedule.registration_start,
            schedule.registration_end,
            schedule.team_formation_start,
            schedule.team_formation_end,
        ),
        participant_limits=before_update.participant_limits,
        tags=before_update.tags,
        tracks=before_update.tracks,
        participant_type=before_update.participant_type,
        venue=before_update.venue,
        team_size=team_size,
        banner=before_update.banner,
        auto_accept=before_update.auto_accept,
        is_archived=before_update.is_archived,
        milestones=before_update.milestones,
        created_at=competition.created_at,
        updated_at=competition.updated_at,
    )


@settings(max_examples=30)
@given(st.data(), valid_schedule_data(), positive_ordered_pairs())
def test_only_owner_can_reschedule(
    gateway: Gateway,
    clock: Clock,
    data: st.DataObject,
    schedule: ScheduleData,
    team_range: tuple[int, int],
) -> None:
    """Only the owning organizer can reschedule a competition."""
    # Arrange
    organizer = gateway.organizer.create()
    different_organizer = gateway.organizer.create()
    competition = data.draw(valid_competition(organizer, clock))
    min_team, max_team = team_range

    # Act / Assert
    with pytest.raises(AccessDeniedError):
        competition.reschedule(
            schedule,
            TeamSizeRange(min=min_team, max=max_team),
            different_organizer,
            clock,
        )


@settings(max_examples=30)
@given(st.data(), valid_schedule_data_no_team_formation(), positive_ordered_pairs())
def test_reschedule_with_team_size_but_no_team_formation_dates_is_rejected(
    gateway: Gateway,
    clock: Clock,
    data: st.DataObject,
    schedule: ScheduleData,
    team_range: tuple[int, int],
) -> None:
    """Rescheduling to team_size set with no team_formation_* dates violates the pairing invariant."""
    # Arrange
    organizer = gateway.organizer.create()
    competition = data.draw(valid_competition(organizer, clock))
    min_team, max_team = team_range

    # Act / Assert
    with pytest.raises(
        InvalidCompetitionDataError,
        match=r"team_size and schedule\.team_formation_\* must be set together",
    ):
        competition.reschedule(schedule, TeamSizeRange(min=min_team, max=max_team), organizer, clock)


@settings(max_examples=30)
@given(st.data(), valid_schedule_data())
def test_reschedule_with_team_formation_dates_but_no_team_size_is_rejected(
    gateway: Gateway,
    clock: Clock,
    data: st.DataObject,
    schedule: ScheduleData,
) -> None:
    """Rescheduling to team_formation_* dates set with no team_size violates the pairing invariant."""
    # Arrange
    organizer = gateway.organizer.create()
    competition = data.draw(valid_competition(organizer, clock))

    # Act / Assert
    with pytest.raises(
        InvalidCompetitionDataError,
        match=r"team_size and schedule\.team_formation_\* must be set together",
    ):
        competition.reschedule(schedule, None, organizer, clock)
