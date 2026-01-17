from datetime import UTC, datetime, timedelta

import pytest

from dreamteams.entities.competition.schedule import (
    CompetitionSchedule,
    ScheduleData,
    normalize_datetime,
    schedule_factory,
)
from dreamteams.entities.errors.competition import InvalidCompetitionDataError


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


def test_schedule_factory_creates_valid_schedule(valid_schedule_data: ScheduleData) -> None:
    """Factory creates schedule with team formation period."""
    schedule = schedule_factory(valid_schedule_data)

    assert schedule == CompetitionSchedule(
        registration_start=valid_schedule_data.registration_start,
        registration_end=valid_schedule_data.registration_end,
        team_formation_start=valid_schedule_data.team_formation_start,
        team_formation_end=valid_schedule_data.team_formation_end,
    )


def test_schedule_factory_creates_valid_schedule_without_team_formation(
    valid_schedule_data_without_team_formation: ScheduleData,
) -> None:
    """Factory creates schedule without team formation period."""
    schedule = schedule_factory(valid_schedule_data_without_team_formation)

    assert schedule == CompetitionSchedule(
        registration_start=valid_schedule_data_without_team_formation.registration_start,
        registration_end=valid_schedule_data_without_team_formation.registration_end,
        team_formation_start=None,
        team_formation_end=None,
    )


def test_schedule_factory_normalizes_datetime() -> None:
    """Factory removes seconds and microseconds from datetime fields."""
    now = datetime.now(tz=UTC)
    data = ScheduleData(
        registration_start=now + timedelta(days=1, hours=8, minutes=30, seconds=45, microseconds=123456),
        registration_end=now + timedelta(days=10, hours=10, minutes=15, seconds=30, microseconds=654321),
        team_formation_start=now + timedelta(days=11, hours=12, minutes=45, seconds=15, microseconds=789012),
        team_formation_end=now + timedelta(days=20, hours=14, minutes=30, seconds=45, microseconds=345678),
    )

    schedule = schedule_factory(data)

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


def test_cannot_create_schedule_with_registration_start_in_past(valid_schedule_data: ScheduleData) -> None:
    """Factory rejects registration start date in the past."""
    valid_schedule_data.registration_start = datetime.now(tz=UTC) - timedelta(days=1)

    with pytest.raises(InvalidCompetitionDataError, match="Registration start date must not be in the past"):
        schedule_factory(valid_schedule_data)


def test_cannot_create_schedule_with_registration_end_in_past(valid_schedule_data: ScheduleData) -> None:
    """Factory rejects registration end date in the past."""
    valid_schedule_data.registration_end = datetime.now(tz=UTC) - timedelta(days=1)

    with pytest.raises(InvalidCompetitionDataError, match="Registration end date must not be in the past"):
        schedule_factory(valid_schedule_data)


def test_cannot_create_schedule_with_registration_start_after_end(valid_schedule_data: ScheduleData) -> None:
    """Factory rejects registration start after end date."""
    valid_schedule_data.registration_start = valid_schedule_data.registration_end + timedelta(days=1)

    with pytest.raises(InvalidCompetitionDataError, match="Registration start date must be before end date"):
        schedule_factory(valid_schedule_data)


def test_cannot_create_schedule_with_registration_start_equal_end(valid_schedule_data: ScheduleData) -> None:
    """Factory rejects registration start equal to end date."""
    same_time = datetime.now(tz=UTC) + timedelta(days=5)
    valid_schedule_data.registration_start = same_time
    valid_schedule_data.registration_end = same_time

    with pytest.raises(InvalidCompetitionDataError, match="Registration start date must be before end date"):
        schedule_factory(valid_schedule_data)


def test_cannot_create_schedule_with_partial_team_formation_start(valid_schedule_data: ScheduleData) -> None:
    """Factory rejects schedule with only team formation start."""
    valid_schedule_data.team_formation_end = None

    with pytest.raises(
        InvalidCompetitionDataError,
        match="Both team formation start and end must be specified together",
    ):
        schedule_factory(valid_schedule_data)


def test_cannot_create_schedule_with_partial_team_formation_end(valid_schedule_data: ScheduleData) -> None:
    """Factory rejects schedule with only team formation end."""
    valid_schedule_data.team_formation_start = None

    with pytest.raises(
        InvalidCompetitionDataError,
        match="Both team formation start and end must be specified together",
    ):
        schedule_factory(valid_schedule_data)


def test_cannot_create_schedule_with_team_formation_start_in_past(valid_schedule_data: ScheduleData) -> None:
    """Factory rejects team formation start date in the past."""
    valid_schedule_data.team_formation_start = datetime.now(tz=UTC) - timedelta(days=1)

    with pytest.raises(InvalidCompetitionDataError, match="Team formation start date must not be in the past"):
        schedule_factory(valid_schedule_data)


def test_cannot_create_schedule_with_team_formation_end_in_past(valid_schedule_data: ScheduleData) -> None:
    """Factory rejects team formation end date in the past."""
    valid_schedule_data.team_formation_end = datetime.now(tz=UTC) - timedelta(days=1)

    with pytest.raises(InvalidCompetitionDataError, match="Team formation end date must not be in the past"):
        schedule_factory(valid_schedule_data)


def test_cannot_create_schedule_with_team_formation_before_registration_end(valid_schedule_data: ScheduleData) -> None:
    """Factory rejects team formation start before registration end."""
    valid_schedule_data.team_formation_start = valid_schedule_data.registration_end - timedelta(days=1)

    with pytest.raises(
        InvalidCompetitionDataError,
        match="Team formation start must be after or equal to registration end",
    ):
        schedule_factory(valid_schedule_data)


def test_cannot_create_schedule_with_team_formation_start_equal_end(valid_schedule_data: ScheduleData) -> None:
    """Factory rejects team formation start equal to end."""
    same_time = datetime.now(tz=UTC) + timedelta(days=15)
    valid_schedule_data.team_formation_start = same_time
    valid_schedule_data.team_formation_end = same_time

    with pytest.raises(InvalidCompetitionDataError, match="Team formation end must be after start"):
        schedule_factory(valid_schedule_data)


def test_schedule_update_changes_all_future_dates() -> None:
    """Update replaces all dates when they are in the future."""
    now = datetime.now(tz=UTC)
    original = CompetitionSchedule(
        registration_start=now + timedelta(days=1),
        registration_end=now + timedelta(days=10),
        team_formation_start=now + timedelta(days=11),
        team_formation_end=now + timedelta(days=20),
    )
    new_data = ScheduleData(
        registration_start=now + timedelta(days=2),
        registration_end=now + timedelta(days=12),
        team_formation_start=now + timedelta(days=13),
        team_formation_end=now + timedelta(days=25),
    )

    updated = original.update(new_data)

    assert updated == CompetitionSchedule(
        registration_start=new_data.registration_start,
        registration_end=new_data.registration_end,
        team_formation_start=new_data.team_formation_start,
        team_formation_end=new_data.team_formation_end,
    )


def test_schedule_update_preserves_past_registration() -> None:
    """Update preserves registration_start and registration_end when they in the past."""
    now = datetime.now(tz=UTC)
    original = CompetitionSchedule(
        registration_start=now - timedelta(days=5),
        registration_end=now - timedelta(days=1),
        team_formation_start=now + timedelta(days=11),
        team_formation_end=now + timedelta(days=20),
    )
    new_data = ScheduleData(
        registration_start=now + timedelta(days=1),
        registration_end=now + timedelta(days=15),
        team_formation_start=now + timedelta(days=16),
        team_formation_end=now + timedelta(days=25),
    )

    updated = original.update(new_data)

    assert updated == CompetitionSchedule(
        registration_start=original.registration_start,
        registration_end=original.registration_end,
        team_formation_start=new_data.team_formation_start,
        team_formation_end=new_data.team_formation_end,
    )


def test_schedule_update_preserves_past_team_formation() -> None:
    """Update preserves team_formation_start and team_formation_end when they in the past."""
    now = datetime.now(tz=UTC)
    original = CompetitionSchedule(
        registration_start=now - timedelta(days=25),
        registration_end=now - timedelta(days=15),
        team_formation_start=now - timedelta(days=5),
        team_formation_end=now - timedelta(days=4),
    )
    new_data = ScheduleData(
        registration_start=now + timedelta(days=1),
        registration_end=now + timedelta(days=15),
        team_formation_start=now + timedelta(days=16),
        team_formation_end=now + timedelta(days=25),
    )

    updated = original.update(new_data)

    assert updated == CompetitionSchedule(
        registration_start=original.registration_start,
        registration_end=original.registration_end,
        team_formation_start=original.team_formation_start,
        team_formation_end=original.team_formation_end,
    )


def test_schedule_update_can_remove_team_formation() -> None:
    """Update allows removing team formation period."""
    now = datetime.now(tz=UTC)
    original = CompetitionSchedule(
        registration_start=now + timedelta(days=1),
        registration_end=now + timedelta(days=10),
        team_formation_start=now + timedelta(days=11),
        team_formation_end=now + timedelta(days=20),
    )
    new_data = ScheduleData(
        registration_start=now + timedelta(days=1),
        registration_end=now + timedelta(days=10),
        team_formation_start=None,
        team_formation_end=None,
    )

    updated = original.update(new_data)

    assert updated.team_formation_start is None
    assert updated.team_formation_end is None


def test_schedule_update_can_add_team_formation() -> None:
    """Update allows adding team formation period."""
    now = datetime.now(tz=UTC)
    original = CompetitionSchedule(
        registration_start=now + timedelta(days=1),
        registration_end=now + timedelta(days=10),
        team_formation_start=None,
        team_formation_end=None,
    )
    new_data = ScheduleData(
        registration_start=now + timedelta(days=1),
        registration_end=now + timedelta(days=10),
        team_formation_start=now + timedelta(days=11),
        team_formation_end=now + timedelta(days=20),
    )

    updated = original.update(new_data)

    assert updated.team_formation_start == normalize_datetime(new_data.team_formation_start)  # type:ignore[arg-type]
    assert updated.team_formation_end == normalize_datetime(new_data.team_formation_end)  # type:ignore[arg-type]
