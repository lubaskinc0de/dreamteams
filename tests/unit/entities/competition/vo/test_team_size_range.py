import pytest

from dreamteams.entities.competition.team_size_range import TeamSizeRange
from dreamteams.entities.errors.competition import InvalidCompetitionDataError


@pytest.mark.parametrize(
    ("max_value", "min_value"),
    [
        (5, 1),  # Standard team size range
        (3, 3),  # Edge case: max equals min (solo teams only)
    ],
)
def test_create_with_valid_values(max_value: int, min_value: int) -> None:
    """Test creating TeamSizeRange with valid values."""
    team_size = TeamSizeRange(max=max_value, min=min_value)

    assert team_size.max == max_value
    assert team_size.min == min_value


@pytest.mark.parametrize(
    ("max_value", "min_value"),
    [
        (5, 0),
        (5, -1),
    ],
)
def test_min_greater_than_zero(max_value: int, min_value: int) -> None:
    """Test that min team size should be > 0."""
    with pytest.raises(InvalidCompetitionDataError, match="Min team size must be at least 1"):
        TeamSizeRange(max=max_value, min=min_value)


@pytest.mark.parametrize(
    ("max_value", "min_value"),
    [
        (0, 1),
        (-5, 1),
    ],
)
def test_max_greater_than_zero(max_value: int, min_value: int) -> None:
    """Test that max team size should be > 0."""
    with pytest.raises(InvalidCompetitionDataError, match="Max team size must be greater than 0"):
        TeamSizeRange(max=max_value, min=min_value)


@pytest.mark.parametrize(
    ("max_value", "min_value"),
    [
        (3, 10),
        (4, 5),
    ],
)
def test_min_not_exceed_max(max_value: int, min_value: int) -> None:
    """Test that max team size should be >= min team size."""
    with pytest.raises(InvalidCompetitionDataError, match="Min team size must be less than or equal to max team size"):
        TeamSizeRange(max=max_value, min=min_value)
