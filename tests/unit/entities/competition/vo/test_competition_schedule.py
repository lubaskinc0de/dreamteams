from datetime import datetime

import pytest
from hypothesis import assume, given
from hypothesis import strategies as st

from dreamteams.entities.common.clock import Clock
from dreamteams.entities.competition.schedule import CompetitionSchedule, ScheduleData, schedule_factory
from dreamteams.entities.errors.competition import InvalidCompetitionDataError
from tests.unit.composite import dt_past, past_schedule, valid_schedule_data


@given(valid_schedule_data())
def test_schedule_factory_creates_valid_schedule(clock: Clock, valid_schedule_data: ScheduleData) -> None:
    """Factory creates schedule with team formation period."""
    schedule = schedule_factory(valid_schedule_data, clock)

    assert schedule == CompetitionSchedule(
        registration_start=valid_schedule_data.registration_start,
        registration_end=valid_schedule_data.registration_end,
        team_formation_start=valid_schedule_data.team_formation_start,
        team_formation_end=valid_schedule_data.team_formation_end,
    )


@given(valid_schedule_data())
def test_schedule_factory_creates_valid_schedule_without_team_formation(
    clock: Clock,
    valid_schedule_data: ScheduleData,
) -> None:
    """Factory creates schedule without team formation period."""
    valid_schedule_data.team_formation_end = None
    valid_schedule_data.team_formation_start = None
    schedule = schedule_factory(valid_schedule_data, clock)

    assert schedule == CompetitionSchedule(
        registration_start=valid_schedule_data.registration_start,
        registration_end=valid_schedule_data.registration_end,
        team_formation_start=None,
        team_formation_end=None,
    )


@given(valid_schedule_data())
def test_schedule_factory_normalizes_datetime(clock: Clock, valid_schedule_data: ScheduleData) -> None:
    """Factory removes seconds and microseconds from datetime fields."""
    schedule = schedule_factory(valid_schedule_data, clock)

    dates: list[datetime | None] = [
        schedule.registration_start,
        schedule.registration_end,
        schedule.team_formation_start,
        schedule.team_formation_end,
    ]
    for date in dates:
        if date is None:
            continue
        assert date.second == 0
        assert date.microsecond == 0


@given(valid_schedule_data(), dt_past())
def test_cannot_create_schedule_with_registration_start_in_past(
    valid_schedule_data: ScheduleData,
    clock: Clock,
) -> None:
    """Factory rejects registration start date in the past."""
    valid_schedule_data.registration_start = dt_past

    with pytest.raises(InvalidCompetitionDataError, match="Registration start date must not be in the past"):
        schedule_factory(valid_schedule_data, clock)


@given(valid_schedule_data(), dt_past())
def test_cannot_create_schedule_with_registration_end_in_past(
    clock: Clock,
    valid_schedule_data: ScheduleData,
    dt_past: datetime,
) -> None:
    """Factory rejects registration end date in the past."""
    valid_schedule_data.registration_end = dt_past

    with pytest.raises(InvalidCompetitionDataError, match="Registration end date must not be in the past"):
        schedule_factory(valid_schedule_data, clock)


@given(valid_schedule_data())
def test_cannot_create_schedule_with_registration_start_after_end(
    valid_schedule_data: ScheduleData,
    clock: Clock,
) -> None:
    """Factory rejects registration start after end date."""
    reg_end = valid_schedule_data.registration_end
    valid_schedule_data.registration_end = valid_schedule_data.registration_start
    valid_schedule_data.registration_start = reg_end

    with pytest.raises(InvalidCompetitionDataError, match="Registration start date must be before end date"):
        schedule_factory(valid_schedule_data, clock)


@given(valid_schedule_data())
def test_cannot_create_schedule_with_registration_start_equal_end(
    valid_schedule_data: ScheduleData,
    clock: Clock,
) -> None:
    """Factory rejects registration start equal to end date."""
    valid_schedule_data.registration_end = valid_schedule_data.registration_start

    with pytest.raises(InvalidCompetitionDataError, match="Registration start date must be before end date"):
        schedule_factory(valid_schedule_data, clock)


@given(valid_schedule_data())
def test_cannot_create_schedule_with_partial_team_formation_start(
    valid_schedule_data: ScheduleData,
    clock: Clock,
) -> None:
    """Factory rejects schedule with only team formation start."""
    valid_schedule_data.team_formation_end = None

    with pytest.raises(
        InvalidCompetitionDataError,
        match="Both team formation start and end must be specified together",
    ):
        schedule_factory(valid_schedule_data, clock)


@given(valid_schedule_data())
def test_cannot_create_schedule_with_partial_team_formation_end(
    valid_schedule_data: ScheduleData,
    clock: Clock,
) -> None:
    """Factory rejects schedule with only team formation end."""
    valid_schedule_data.team_formation_start = None

    with pytest.raises(
        InvalidCompetitionDataError,
        match="Both team formation start and end must be specified together",
    ):
        schedule_factory(valid_schedule_data, clock)


@given(valid_schedule_data(), dt_past())
def test_cannot_create_schedule_with_team_formation_start_in_past(
    valid_schedule_data: ScheduleData,
    clock: Clock,
) -> None:
    """Factory rejects team formation start date in the past."""
    valid_schedule_data.team_formation_start = dt_past

    with pytest.raises(InvalidCompetitionDataError, match="Team formation start date must not be in the past"):
        schedule_factory(valid_schedule_data, clock)


@given(valid_schedule_data(), dt_past())
def test_cannot_create_schedule_with_team_formation_end_in_past(
    valid_schedule_data: ScheduleData,
    clock: Clock,
) -> None:
    """Factory rejects team formation end date in the past."""
    valid_schedule_data.team_formation_end = dt_past

    with pytest.raises(InvalidCompetitionDataError, match="Team formation end date must not be in the past"):
        schedule_factory(valid_schedule_data, clock)


@given(valid_schedule_data())
def test_cannot_create_schedule_with_team_formation_before_registration_end(
    valid_schedule_data: ScheduleData,
    clock: Clock,
) -> None:
    """Factory rejects team formation start before registration end."""
    valid_schedule_data.team_formation_start = valid_schedule_data.registration_start

    with pytest.raises(
        InvalidCompetitionDataError,
        match="Team formation start must be after or equal to registration end",
    ):
        schedule_factory(valid_schedule_data, clock)


@given(valid_schedule_data())
def test_cannot_create_schedule_with_team_formation_start_equal_end(
    valid_schedule_data: ScheduleData,
    clock: Clock,
) -> None:
    """Factory rejects team formation start equal to end."""
    valid_schedule_data.team_formation_start = valid_schedule_data.team_formation_end

    with pytest.raises(InvalidCompetitionDataError, match="Team formation end must be after start"):
        schedule_factory(valid_schedule_data, clock)


@given(valid_schedule_data(), st.data())
def test_schedule_update_changes_all_future_dates(clock: Clock, orig_data: ScheduleData, data: st.DataObject) -> None:
    """Update replaces all dates when they are in the future."""
    assume(orig_data.team_formation_end is not None)
    orig = CompetitionSchedule(
        registration_start=orig_data.registration_start,
        team_formation_start=orig_data.team_formation_start,
        team_formation_end=orig_data.team_formation_end,
        registration_end=orig_data.registration_end,
    )
    new_data = data.draw(valid_schedule_data(min_dt=orig_data.team_formation_end.replace(tzinfo=None)))  # type:ignore[union-attr]

    updated = orig.update(new_data, clock)

    assert updated == CompetitionSchedule(
        registration_start=new_data.registration_start,
        registration_end=new_data.registration_end,
        team_formation_start=new_data.team_formation_start,
        team_formation_end=new_data.team_formation_end,
    )


@given(valid_schedule_data(), past_schedule())
def test_schedule_update_preserves_past_dates(
    clock: Clock,
    valid_schedule_data: ScheduleData,
    past_schedule: CompetitionSchedule,
) -> None:
    """Update preserves dates when they in the past."""
    updated = past_schedule.update(valid_schedule_data, clock)

    assert updated == CompetitionSchedule(
        registration_start=past_schedule.registration_start,
        registration_end=past_schedule.registration_end,
        team_formation_start=past_schedule.team_formation_start,
        team_formation_end=past_schedule.team_formation_end,
    )
