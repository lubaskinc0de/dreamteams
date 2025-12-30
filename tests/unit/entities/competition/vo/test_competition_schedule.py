from datetime import UTC, datetime, timedelta

import pytest

from dreamteams.entities.competition import CompetitionSchedule
from dreamteams.entities.errors.competition import InvalidCompetitionDataError


@pytest.mark.parametrize(
    ("reg_start_offset", "reg_end_offset", "comp_start_offset", "comp_end_offset"),
    [
        (1, 10, 11, 15),
        (1, 10, 10, 15),
    ],
)
def test_create_with_valid_dates(
    reg_start_offset: int,
    reg_end_offset: int,
    comp_start_offset: int,
    comp_end_offset: int,
) -> None:
    """Test creating CompetitionSchedule with valid date combinations."""
    now = datetime.now(tz=UTC)
    reg_start = now + timedelta(days=reg_start_offset)
    reg_end = now + timedelta(days=reg_end_offset)
    comp_start = now + timedelta(days=comp_start_offset)
    comp_end = now + timedelta(days=comp_end_offset)

    schedule = CompetitionSchedule(
        registration_start=reg_start,
        registration_end=reg_end,
        competition_start=comp_start,
        competition_end=comp_end,
    )

    assert schedule.registration_start == reg_start
    assert schedule.registration_end == reg_end
    assert schedule.competition_start == comp_start
    assert schedule.competition_end == comp_end


@pytest.mark.parametrize(
    ("reg_start_offset", "reg_end_offset", "comp_start_offset", "comp_end_offset", "expected_error"),
    [
        (-1, 10, 11, 15, "Registration start date must not be in the past"),
        (1, -1, 11, 15, "Registration end date must not be in the past"),
        (1, 10, -1, 15, "Competition start date must not be in the past"),
        (1, 10, 11, -1, "Competition end date must not be in the past"),
        (1, 10, 15, 11, "End date must be after start date"),
        (1, 10, 11, 11, "End date must be after start date"),
        (10, 1, 11, 15, "Registration start date must be before end date"),
        (5, 5, 11, 15, "Registration start date must be before end date"),
        (1, 15, 11, 20, "Registration end date must be before or equal to start date"),
    ],
)
def test_create_with_invalid_dates_raises_error(
    reg_start_offset: int,
    reg_end_offset: int,
    comp_start_offset: int,
    comp_end_offset: int,
    expected_error: str,
) -> None:
    """Test that invalid date combinations raise appropriate errors."""
    now = datetime.now(tz=UTC)
    reg_start = now + timedelta(days=reg_start_offset)
    reg_end = now + timedelta(days=reg_end_offset)
    comp_start = now + timedelta(days=comp_start_offset)
    comp_end = now + timedelta(days=comp_end_offset)

    with pytest.raises(InvalidCompetitionDataError, match=expected_error):
        CompetitionSchedule(
            registration_start=reg_start,
            registration_end=reg_end,
            competition_start=comp_start,
            competition_end=comp_end,
        )
