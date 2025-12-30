import pytest

from dreamteams.entities.competition import TeamSizeRange
from dreamteams.entities.errors.competition import InvalidCompetitionDataError


@pytest.mark.parametrize(
    ("max_value", "min_value"),
    [
        (5, 1),
        (3, 3),
    ],
)
def test_create_with_valid_values(max_value: int, min_value: int) -> None:
    """Test creating TeamSizeRange with valid values."""
    team_size = TeamSizeRange(max=max_value, min=min_value)

    assert team_size.max == max_value
    assert team_size.min == min_value


@pytest.mark.parametrize(
    ("max_value", "min_value", "expected_error"),
    [
        (5, 0, "Min team size must be at least 1"),
        (0, 1, "Max team size must be greater than 0"),
        (-5, 1, "Max team size must be greater than 0"),
        (3, 10, "Min team size must be less than or equal to max team size"),
    ],
)
def test_create_with_invalid_values_raises_error(max_value: int, min_value: int, expected_error: str) -> None:
    """Test that invalid values raise appropriate errors."""
    with pytest.raises(InvalidCompetitionDataError, match=expected_error):
        TeamSizeRange(max=max_value, min=min_value)
