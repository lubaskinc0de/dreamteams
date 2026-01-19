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
    ("max_value", "min_value"),
    [
        (0, 1),
        (-10, 5),
    ],
)
def test_max_greater_than_zero(max_value: int, min_value: int) -> None:
    """Test that max value must be > 0."""
    with pytest.raises(InvalidCompetitionDataError, match="Max participants must be greater than 0"):
        ParticipantLimits(max=max_value, min=min_value)


@pytest.mark.parametrize(
    ("max_value", "min_value"),
    [
        (100, 0),
        (100, -5),
    ],
)
def test_min_greater_than_zero(max_value: int, min_value: int) -> None:
    """Test that min value must be > 0."""
    with pytest.raises(InvalidCompetitionDataError, match="Min participants must be greater than 0"):
        ParticipantLimits(max=max_value, min=min_value)


@pytest.mark.parametrize(
    ("max_value", "min_value"),
    [
        (10, 50),
        (39, 40),
    ],
)
def test_min_not_exceed_max(max_value: int, min_value: int) -> None:
    """Test that min value <= max value."""
    with pytest.raises(
        InvalidCompetitionDataError, match="Min participants must be less than or equal to max participants",
    ):
        ParticipantLimits(max=max_value, min=min_value)
