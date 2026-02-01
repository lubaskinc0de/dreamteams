from datetime import datetime, timedelta

import pytest
from freezegun import freeze_time

from dreamteams.entities.common.clock import Clock
from dreamteams.entities.common.datetime_utils import normalize_datetime
from dreamteams.entities.competition.schedule import CompetitionSchedule, ScheduleData, schedule_factory
from dreamteams.entities.errors.competition import InvalidCompetitionDataError
from tests.unit.entities.competition.conftest import utc


@pytest.fixture
def valid_schedule_data_without_team_formation(
    valid_schedule_data: ScheduleData,
) -> ScheduleData:
    """Valid schedule data without team formation period."""
    return ScheduleData(
        registration_start=valid_schedule_data.registration_start,
        registration_end=valid_schedule_data.registration_end,
        team_formation_start=None,
        team_formation_end=None,
    )


@freeze_time("2025-01-15 12:00:00")
def test_schedule_factory_creates_valid_schedule(valid_schedule_data: ScheduleData, clock: Clock) -> None:
    """Factory creates schedule with team formation period."""
    schedule = schedule_factory(valid_schedule_data, clock)

    assert schedule == CompetitionSchedule(
        registration_start=valid_schedule_data.registration_start,
        registration_end=valid_schedule_data.registration_end,
        team_formation_start=valid_schedule_data.team_formation_start,
        team_formation_end=valid_schedule_data.team_formation_end,
    )


@freeze_time("2025-01-15 12:00:00")
def test_schedule_factory_creates_valid_schedule_without_team_formation(
    valid_schedule_data_without_team_formation: ScheduleData,
    clock: Clock,
) -> None:
    """Factory creates schedule without team formation period."""
    schedule = schedule_factory(valid_schedule_data_without_team_formation, clock)

    assert schedule == CompetitionSchedule(
        registration_start=valid_schedule_data_without_team_formation.registration_start,
        registration_end=valid_schedule_data_without_team_formation.registration_end,
        team_formation_start=None,
        team_formation_end=None,
    )


@freeze_time("2025-01-15 12:00:00")
def test_schedule_factory_normalizes_datetime(clock: Clock) -> None:
    """Factory removes seconds and microseconds from datetime fields."""
    data = ScheduleData(
        registration_start=utc("2026-01-20 10:30:45").replace(microsecond=123456),
        registration_end=utc("2026-02-01 18:15:30").replace(microsecond=654321),
        team_formation_start=utc("2026-02-05 10:45:15").replace(microsecond=789012),
        team_formation_end=utc("2026-02-15 18:30:45").replace(microsecond=345678),
    )

    schedule = schedule_factory(data, clock)

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


@freeze_time("2025-01-15 12:00:00")
def test_cannot_create_schedule_with_registration_start_in_past(
    valid_schedule_data: ScheduleData,
    clock: Clock,
) -> None:
    """Factory rejects registration start date in the past."""
    valid_schedule_data.registration_start = utc("2024-12-01 10:00:00")

    with pytest.raises(InvalidCompetitionDataError, match="Registration start date must not be in the past"):
        schedule_factory(valid_schedule_data, clock)


@freeze_time("2025-01-15 12:00:00")
def test_cannot_create_schedule_with_registration_end_in_past(valid_schedule_data: ScheduleData, clock: Clock) -> None:
    """Factory rejects registration end date in the past."""
    valid_schedule_data.registration_end = utc("2024-12-01 10:00:00")

    with pytest.raises(InvalidCompetitionDataError, match="Registration end date must not be in the past"):
        schedule_factory(valid_schedule_data, clock)


@freeze_time("2025-01-15 12:00:00")
def test_cannot_create_schedule_with_registration_start_after_end(
    valid_schedule_data: ScheduleData,
    clock: Clock,
) -> None:
    """Factory rejects registration start after end date."""
    valid_schedule_data.registration_start = valid_schedule_data.registration_end + timedelta(days=1)

    with pytest.raises(InvalidCompetitionDataError, match="Registration start date must be before end date"):
        schedule_factory(valid_schedule_data, clock)


@freeze_time("2025-01-15 12:00:00")
def test_cannot_create_schedule_with_registration_start_equal_end(
    valid_schedule_data: ScheduleData,
    clock: Clock,
) -> None:
    """Factory rejects registration start equal to end date."""
    same_time = utc("2026-01-25 10:00:00")
    valid_schedule_data.registration_start = same_time
    valid_schedule_data.registration_end = same_time

    with pytest.raises(InvalidCompetitionDataError, match="Registration start date must be before end date"):
        schedule_factory(valid_schedule_data, clock)


@freeze_time("2025-01-15 12:00:00")
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


@freeze_time("2025-01-15 12:00:00")
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


@freeze_time("2025-01-15 12:00:00")
def test_cannot_create_schedule_with_team_formation_start_in_past(
    valid_schedule_data: ScheduleData,
    clock: Clock,
) -> None:
    """Factory rejects team formation start date in the past."""
    valid_schedule_data.team_formation_start = utc("2024-12-01 10:00:00")

    with pytest.raises(InvalidCompetitionDataError, match="Team formation start date must not be in the past"):
        schedule_factory(valid_schedule_data, clock)


@freeze_time("2025-01-15 12:00:00")
def test_cannot_create_schedule_with_team_formation_end_in_past(
    valid_schedule_data: ScheduleData,
    clock: Clock,
) -> None:
    """Factory rejects team formation end date in the past."""
    valid_schedule_data.team_formation_end = utc("2024-12-01 10:00:00")

    with pytest.raises(InvalidCompetitionDataError, match="Team formation end date must not be in the past"):
        schedule_factory(valid_schedule_data, clock)


@freeze_time("2025-01-15 12:00:00")
def test_cannot_create_schedule_with_team_formation_before_registration_end(
    valid_schedule_data: ScheduleData,
    clock: Clock,
) -> None:
    """Factory rejects team formation start before registration end."""
    valid_schedule_data.team_formation_start = valid_schedule_data.registration_end - timedelta(days=1)

    with pytest.raises(
        InvalidCompetitionDataError,
        match="Team formation start must be after or equal to registration end",
    ):
        schedule_factory(valid_schedule_data, clock)


@freeze_time("2025-01-15 12:00:00")
def test_cannot_create_schedule_with_team_formation_start_equal_end(
    valid_schedule_data: ScheduleData,
    clock: Clock,
) -> None:
    """Factory rejects team formation start equal to end."""
    same_time = utc("2026-02-10 10:00:00")
    valid_schedule_data.team_formation_start = same_time
    valid_schedule_data.team_formation_end = same_time

    with pytest.raises(InvalidCompetitionDataError, match="Team formation end must be after start"):
        schedule_factory(valid_schedule_data, clock)


@freeze_time("2025-01-15 12:00:00")
def test_schedule_update_changes_all_future_dates(clock: Clock) -> None:
    """Update replaces all dates when they are in the future."""
    original = CompetitionSchedule(
        registration_start=utc("2026-01-20 10:00:00"),
        registration_end=utc("2026-02-01 18:00:00"),
        team_formation_start=utc("2026-02-05 10:00:00"),
        team_formation_end=utc("2026-02-15 18:00:00"),
    )
    new_data = ScheduleData(
        registration_start=utc("2026-01-25 10:00:00"),
        registration_end=utc("2026-02-05 18:00:00"),
        team_formation_start=utc("2026-02-10 10:00:00"),
        team_formation_end=utc("2026-02-28 18:00:00"),
    )

    updated = original.update(new_data, clock)

    assert updated == CompetitionSchedule(
        registration_start=new_data.registration_start,
        registration_end=new_data.registration_end,
        team_formation_start=new_data.team_formation_start,
        team_formation_end=new_data.team_formation_end,
    )


@freeze_time("2025-01-15 12:00:00")
def test_schedule_update_preserves_past_registration(clock: Clock) -> None:
    """Update preserves registration_start and registration_end when they in the past."""
    original = CompetitionSchedule(
        registration_start=utc("2024-12-01 10:00:00"),
        registration_end=utc("2024-12-20 18:00:00"),
        team_formation_start=utc("2026-02-05 10:00:00"),
        team_formation_end=utc("2026-02-15 18:00:00"),
    )
    new_data = ScheduleData(
        registration_start=utc("2026-01-20 10:00:00"),
        registration_end=utc("2026-02-01 18:00:00"),
        team_formation_start=utc("2026-02-10 10:00:00"),
        team_formation_end=utc("2026-02-28 18:00:00"),
    )

    updated = original.update(new_data, clock)

    assert updated == CompetitionSchedule(
        registration_start=original.registration_start,
        registration_end=original.registration_end,
        team_formation_start=new_data.team_formation_start,
        team_formation_end=new_data.team_formation_end,
    )


@freeze_time("2025-01-15 12:00:00")
def test_schedule_update_preserves_past_team_formation(clock: Clock) -> None:
    """Update preserves team_formation_start and team_formation_end when they in the past."""
    original = CompetitionSchedule(
        registration_start=utc("2024-11-01 10:00:00"),
        registration_end=utc("2024-11-20 18:00:00"),
        team_formation_start=utc("2024-12-01 10:00:00"),
        team_formation_end=utc("2024-12-15 18:00:00"),
    )
    new_data = ScheduleData(
        registration_start=utc("2026-01-20 10:00:00"),
        registration_end=utc("2026-02-01 18:00:00"),
        team_formation_start=utc("2026-02-10 10:00:00"),
        team_formation_end=utc("2026-02-28 18:00:00"),
    )

    updated = original.update(new_data, clock)

    assert updated == CompetitionSchedule(
        registration_start=original.registration_start,
        registration_end=original.registration_end,
        team_formation_start=original.team_formation_start,
        team_formation_end=original.team_formation_end,
    )


@freeze_time("2025-01-15 12:00:00")
def test_schedule_update_can_remove_team_formation(clock: Clock) -> None:
    """Update allows removing team formation period."""
    original = CompetitionSchedule(
        registration_start=utc("2026-01-20 10:00:00"),
        registration_end=utc("2026-02-01 18:00:00"),
        team_formation_start=utc("2026-02-05 10:00:00"),
        team_formation_end=utc("2026-02-15 18:00:00"),
    )
    new_data = ScheduleData(
        registration_start=utc("2026-01-20 10:00:00"),
        registration_end=utc("2026-02-01 18:00:00"),
        team_formation_start=None,
        team_formation_end=None,
    )

    updated = original.update(new_data, clock)

    assert updated.team_formation_start is None
    assert updated.team_formation_end is None


@freeze_time("2025-01-15 12:00:00")
def test_schedule_update_can_add_team_formation(clock: Clock) -> None:
    """Update allows adding team formation period."""
    original = CompetitionSchedule(
        registration_start=utc("2026-01-20 10:00:00"),
        registration_end=utc("2026-02-01 18:00:00"),
        team_formation_start=None,
        team_formation_end=None,
    )
    new_data = ScheduleData(
        registration_start=utc("2026-01-20 10:00:00"),
        registration_end=utc("2026-02-01 18:00:00"),
        team_formation_start=utc("2026-02-05 10:00:00"),
        team_formation_end=utc("2026-02-15 18:00:00"),
    )

    updated = original.update(new_data, clock)

    assert updated.team_formation_start == normalize_datetime(new_data.team_formation_start)  # type:ignore[arg-type]
    assert updated.team_formation_end == normalize_datetime(new_data.team_formation_end)  # type:ignore[arg-type]
