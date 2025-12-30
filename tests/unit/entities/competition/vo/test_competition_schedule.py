from datetime import UTC, datetime, timedelta

import pytest

from dreamteams.entities.competition import CompetitionSchedule, normalize_datetime
from dreamteams.entities.errors.competition import InvalidCompetitionDataError


@pytest.mark.parametrize(
    ("reg_start", "reg_end", "comp_start", "comp_end", "tf_start", "tf_end"),
    [
        # Without team formation period
        (
            timedelta(days=1, hours=8),    # registration starts in 1 day
            timedelta(days=10, hours=10),  # registration ends in 10 days
            timedelta(days=11, hours=14),  # competition starts in 11 days
            timedelta(days=15, hours=18),  # competition ends in 15 days
            None,                          # no team formation start
            None,                          # no team formation end
        ),
        # Registration end same day as competition start (but earlier time)
        (
            timedelta(days=1, hours=8),    # registration starts in 1 day at 8:00
            timedelta(days=10, hours=10),  # registration ends in 10 days at 10:00
            timedelta(days=10, hours=14),  # competition starts same day at 14:00 (after registration)
            timedelta(days=15, hours=18),  # competition ends in 15 days
            None,                          # no team formation start
            None,                          # no team formation end
        ),
        # With team formation: starts after competition start
        (
            timedelta(days=1, hours=8),    # registration starts in 1 day
            timedelta(days=10, hours=10),  # registration ends in 10 days
            timedelta(days=11, hours=14),  # competition starts in 11 days
            timedelta(days=15, hours=18),  # competition ends in 15 days
            timedelta(days=11, hours=16),  # team formation starts after competition start
            timedelta(days=12, hours=18),  # team formation ends in 12 days
        ),
        # With team formation: spans until competition end
        (
            timedelta(days=1, hours=8),    # registration starts in 1 day
            timedelta(days=10, hours=10),  # registration ends in 10 days
            timedelta(days=11, hours=14),  # competition starts in 11 days
            timedelta(days=15, hours=18),  # competition ends in 15 days
            timedelta(days=11, hours=16),  # team formation starts after competition start
            timedelta(days=15, hours=17),  # team formation ends on competition end day (before competition ends)
        ),
        # With team formation: starts on registration end day (but later time)
        (
            timedelta(days=1, hours=8),    # registration starts in 1 day
            timedelta(days=10, hours=10),  # registration ends in 10 days at 10:00
            timedelta(days=11, hours=14),  # competition starts in 11 days
            timedelta(days=15, hours=18),  # competition ends in 15 days
            timedelta(days=10, hours=12),  # team formation starts same day as registration end (at 12:00)
            timedelta(days=12, hours=16),  # team formation ends in 12 days
        ),
        # With team formation: starts on registration end day and ends on competition end day
        (
            timedelta(days=1, hours=8),    # registration starts in 1 day
            timedelta(days=10, hours=10),  # registration ends in 10 days
            timedelta(days=11, hours=14),  # competition starts in 11 days
            timedelta(days=15, hours=18),  # competition ends in 15 days
            timedelta(days=10, hours=12),  # team formation starts same day as registration end
            timedelta(days=15, hours=17),  # team formation ends same day as competition end
        ),
    ],
)
def test_create_with_valid_dates(
    reg_start: timedelta,
    reg_end: timedelta,
    comp_start: timedelta,
    comp_end: timedelta,
    tf_start: timedelta | None,
    tf_end: timedelta | None,
) -> None:
    """Test creating CompetitionSchedule with valid date combinations."""
    now = datetime.now(tz=UTC)
    reg_start_dt = now + reg_start
    reg_end_dt = now + reg_end
    comp_start_dt = now + comp_start
    comp_end_dt = now + comp_end
    tf_start_dt = now + tf_start if tf_start is not None else None
    tf_end_dt = now + tf_end if tf_end is not None else None

    schedule = CompetitionSchedule(
        registration_start=reg_start_dt,
        registration_end=reg_end_dt,
        competition_start=comp_start_dt,
        competition_end=comp_end_dt,
        team_formation_start=tf_start_dt,
        team_formation_end=tf_end_dt,
    )

    # CompetitionSchedule normalizes datetimes by removing seconds and microseconds
    assert schedule.registration_start == normalize_datetime(reg_start_dt)
    assert schedule.registration_end == normalize_datetime(reg_end_dt)
    assert schedule.competition_start == normalize_datetime(comp_start_dt)
    assert schedule.competition_end == normalize_datetime(comp_end_dt)

    if tf_start_dt is not None and tf_end_dt is not None:
        assert schedule.team_formation_start == normalize_datetime(tf_start_dt)
        assert schedule.team_formation_end == normalize_datetime(tf_end_dt)
    else:
        assert schedule.team_formation_start is None
        assert schedule.team_formation_end is None


def test_datetime_normalization() -> None:
    """Test that seconds and microseconds are removed from all datetime fields."""
    now = datetime.now(tz=UTC)
    reg_start = now + timedelta(days=1, hours=8, minutes=30, seconds=45, microseconds=123456)
    reg_end = now + timedelta(days=10, hours=10, minutes=15, seconds=30, microseconds=654321)
    comp_start = now + timedelta(days=11, hours=14, minutes=0, seconds=10, microseconds=111111)
    comp_end = now + timedelta(days=15, hours=18, minutes=45, seconds=59, microseconds=999999)

    schedule = CompetitionSchedule(
        registration_start=reg_start,
        registration_end=reg_end,
        competition_start=comp_start,
        competition_end=comp_end,
    )

    assert schedule.registration_start == normalize_datetime(reg_start)
    assert schedule.registration_end == normalize_datetime(reg_end)
    assert schedule.competition_start == normalize_datetime(comp_start)
    assert schedule.competition_end == normalize_datetime(comp_end)
    assert schedule.registration_start.second == 0
    assert schedule.registration_start.microsecond == 0


@pytest.mark.parametrize(
    ("reg_start", "reg_end", "comp_start", "comp_end", "tf_start", "tf_end", "expected_error"),
    [
        # Registration start in the past
        (
            timedelta(days=-1, hours=8),   # registration starts in the PAST (invalid)
            timedelta(days=10, hours=10),  # registration ends in 10 days
            timedelta(days=11, hours=14),  # competition starts in 11 days
            timedelta(days=15, hours=18),  # competition ends in 15 days
            None,                          # no team formation start
            None,                          # no team formation end
            "Registration start date must not be in the past",
        ),
        # Registration end in the past
        (
            timedelta(days=1, hours=8),    # registration starts in 1 day
            timedelta(days=-1, hours=10),  # registration ends in the PAST (invalid)
            timedelta(days=11, hours=14),  # competition starts in 11 days
            timedelta(days=15, hours=18),  # competition ends in 15 days
            None,                          # no team formation start
            None,                          # no team formation end
            "Registration end date must not be in the past",
        ),
        # Competition start in the past
        (
            timedelta(days=1, hours=8),    # registration starts in 1 day
            timedelta(days=10, hours=10),  # registration ends in 10 days
            timedelta(days=-1, hours=14),  # competition starts in the PAST (invalid)
            timedelta(days=15, hours=18),  # competition ends in 15 days
            None,                          # no team formation start
            None,                          # no team formation end
            "Competition start date must not be in the past",
        ),
        # Competition end in the past
        (
            timedelta(days=1, hours=8),    # registration starts in 1 day
            timedelta(days=10, hours=10),  # registration ends in 10 days
            timedelta(days=11, hours=14),  # competition starts in 11 days
            timedelta(days=-1, hours=18),  # competition ends in the PAST (invalid)
            None,                          # no team formation start
            None,                          # no team formation end
            "Competition end date must not be in the past",
        ),
        # Competition end before competition start
        (
            timedelta(days=1, hours=8),    # registration starts in 1 day
            timedelta(days=10, hours=10),  # registration ends in 10 days
            timedelta(days=15, hours=14),  # competition starts in 15 days
            timedelta(days=11, hours=18),  # competition ends in 11 days (BEFORE start - invalid)
            None,                          # no team formation start
            None,                          # no team formation end
            "End date must be after start date",
        ),
        # Competition end equals competition start
        (
            timedelta(days=1, hours=8),    # registration starts in 1 day
            timedelta(days=10, hours=10),  # registration ends in 10 days
            timedelta(days=11, hours=14),  # competition starts in 11 days
            timedelta(days=11, hours=14),  # competition ends at SAME TIME as start (invalid)
            None,                          # no team formation start
            None,                          # no team formation end
            "End date must be after start date",
        ),
        # Registration start after registration end
        (
            timedelta(days=10, hours=8),   # registration starts in 10 days
            timedelta(days=1, hours=10),   # registration ends in 1 day (BEFORE start - invalid)
            timedelta(days=11, hours=14),  # competition starts in 11 days
            timedelta(days=15, hours=18),  # competition ends in 15 days
            None,                          # no team formation start
            None,                          # no team formation end
            "Registration start date must be before end date",
        ),
        # Registration start equals registration end
        (
            timedelta(days=5, hours=8),    # registration starts in 5 days
            timedelta(days=5, hours=8),    # registration ends at SAME TIME (invalid)
            timedelta(days=11, hours=14),  # competition starts in 11 days
            timedelta(days=15, hours=18),  # competition ends in 15 days
            None,                          # no team formation start
            None,                          # no team formation end
            "Registration start date must be before end date",
        ),
        # Registration end after competition start
        (
            timedelta(days=1, hours=8),    # registration starts in 1 day
            timedelta(days=15, hours=10),  # registration ends in 15 days (AFTER competition start - invalid)
            timedelta(days=11, hours=14),  # competition starts in 11 days
            timedelta(days=20, hours=18),  # competition ends in 20 days
            None,                          # no team formation start
            None,                          # no team formation end
            "Registration end date must be before or equal to start date",
        ),
        # Team formation start specified but end is None
        (
            timedelta(days=1, hours=8),    # registration starts in 1 day
            timedelta(days=10, hours=10),  # registration ends in 10 days
            timedelta(days=11, hours=14),  # competition starts in 11 days
            timedelta(days=15, hours=18),  # competition ends in 15 days
            None,                          # team formation start is None (invalid - must specify both or neither)
            timedelta(days=12, hours=16),  # team formation end is specified
            "Both team formation start and end must be specified together",
        ),
        # Team formation end specified but start is None
        (
            timedelta(days=1, hours=8),    # registration starts in 1 day
            timedelta(days=10, hours=10),  # registration ends in 10 days
            timedelta(days=11, hours=14),  # competition starts in 11 days
            timedelta(days=15, hours=18),  # competition ends in 15 days
            timedelta(days=11, hours=12),  # team formation start is specified
            None,                          # team formation end is None (invalid - must specify both or neither)
            "Both team formation start and end must be specified together",
        ),
        # Team formation start in the past
        (
            timedelta(days=1, hours=8),    # registration starts in 1 day
            timedelta(days=10, hours=10),  # registration ends in 10 days
            timedelta(days=11, hours=14),  # competition starts in 11 days
            timedelta(days=15, hours=18),  # competition ends in 15 days
            timedelta(days=-1, hours=12),  # team formation starts in the PAST (invalid)
            timedelta(days=12, hours=16),  # team formation ends in 12 days
            "Team formation start date must not be in the past",
        ),
        # Team formation end in the past
        (
            timedelta(days=1, hours=8),    # registration starts in 1 day
            timedelta(days=10, hours=10),  # registration ends in 10 days
            timedelta(days=11, hours=14),  # competition starts in 11 days
            timedelta(days=15, hours=18),  # competition ends in 15 days
            timedelta(days=11, hours=12),  # team formation starts in 11 days
            timedelta(days=-1, hours=16),  # team formation ends in the PAST (invalid)
            "Team formation end date must not be in the past",
        ),
        # Team formation start before registration end
        (
            timedelta(days=1, hours=8),    # registration starts in 1 day
            timedelta(days=10, hours=10),  # registration ends in 10 days
            timedelta(days=11, hours=14),  # competition starts in 11 days
            timedelta(days=15, hours=18),  # competition ends in 15 days
            timedelta(days=9, hours=12),   # team formation starts in 9 days (BEFORE registration end - invalid)
            timedelta(days=12, hours=16),  # team formation ends in 12 days
            "Team formation start must be after or equal to registration end",
        ),
        # Team formation end equals team formation start
        (
            timedelta(days=1, hours=8),    # registration starts in 1 day
            timedelta(days=10, hours=10),  # registration ends in 10 days
            timedelta(days=11, hours=14),  # competition starts in 11 days
            timedelta(days=15, hours=18),  # competition ends in 15 days
            timedelta(days=11, hours=12),  # team formation starts in 11 days
            timedelta(days=11, hours=12),  # team formation ends at SAME TIME as start (invalid)
            "Team formation end must be after start",
        ),
        # Team formation end after competition end
        (
            timedelta(days=1, hours=8),    # registration starts in 1 day
            timedelta(days=10, hours=10),  # registration ends in 10 days
            timedelta(days=11, hours=14),  # competition starts in 11 days
            timedelta(days=15, hours=18),  # competition ends in 15 days
            timedelta(days=11, hours=12),  # team formation starts in 11 days
            timedelta(days=16, hours=16),  # team formation ends in 16 days (AFTER competition end - invalid)
            "Team formation end must be before or equal to competition end",
        ),
    ],
)
def test_create_with_invalid_dates_raises_error(
    reg_start: timedelta,
    reg_end: timedelta,
    comp_start: timedelta,
    comp_end: timedelta,
    tf_start: timedelta | None,
    tf_end: timedelta | None,
    expected_error: str,
) -> None:
    """Test that invalid date combinations raise appropriate errors."""
    now = datetime.now(tz=UTC)
    reg_start_dt = now + reg_start
    reg_end_dt = now + reg_end
    comp_start_dt = now + comp_start
    comp_end_dt = now + comp_end
    tf_start_dt = now + tf_start if tf_start is not None else None
    tf_end_dt = now + tf_end if tf_end is not None else None

    with pytest.raises(InvalidCompetitionDataError, match=expected_error):
        CompetitionSchedule(
            registration_start=reg_start_dt,
            registration_end=reg_end_dt,
            competition_start=comp_start_dt,
            competition_end=comp_end_dt,
            team_formation_start=tf_start_dt,
            team_formation_end=tf_end_dt,
        )
