import pytest

from dreamteams.entities.competition.participant_limits import ParticipantLimits
from dreamteams.entities.errors.competition import InvalidCompetitionDataError


@pytest.mark.parametrize(
    ("max_value", "min_value"),
    [
        (100, 10),  # Standard case: max > min
        (50, 50),  # Edge case: max equals min
        (50, 1),  # Min is minimum possible value
    ],
)
def test_create_with_valid_values(max_value: int, min_value: int) -> None:
    """Test creating ParticipantLimits with valid values."""
    limits = ParticipantLimits(max=max_value, min=min_value)

    assert limits.max == max_value
    assert limits.min == min_value


@pytest.mark.parametrize(
    ("max_value", "min_value", "expected_error"),
    [
        # Max must be greater than 0
        (0, 1, "Max participants must be greater than 0"),
        (-10, 5, "Max participants must be greater than 0"),
        # Min must be greater than 0
        (100, 0, "Min participants must be greater than 0"),
        (100, -5, "Min participants must be greater than 0"),
        # Min must not exceed max
        (10, 50, "Min participants must be less than or equal to max participants"),
    ],
)
def test_create_with_invalid_values_raises_error(max_value: int, min_value: int, expected_error: str) -> None:
    """Test that invalid values raise appropriate errors."""
    with pytest.raises(InvalidCompetitionDataError, match=expected_error):
        ParticipantLimits(max=max_value, min=min_value)
