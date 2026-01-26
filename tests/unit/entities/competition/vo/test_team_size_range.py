import pytest
from hypothesis import given
from hypothesis import strategies as st

from dreamteams.entities.competition.team_size_range import TeamSizeRange
from dreamteams.entities.errors.competition import InvalidCompetitionDataError
from tests.unit.helpers import ordered_pairs


@given(ordered_pairs().filter(lambda pair: pair[0] > 0 and pair[1] > 0))
def test_create_team_size_with_valid_values(pair: tuple[int, int]) -> None:
    """Test creating TeamSizeRange with valid values."""
    min_value, max_value = pair
    team_size = TeamSizeRange(max=max_value, min=min_value)

    assert team_size.max == max_value
    assert team_size.min == min_value


@given(ordered_pairs().filter(lambda pair: pair[0] <= 0))
def test_team_size_min_greater_than_zero(pair: tuple[int, int]) -> None:
    """Test that min team size should be > 0."""
    min_value, max_value = pair
    with pytest.raises(InvalidCompetitionDataError, match="Min team size must be at least 1"):
        TeamSizeRange(max=max_value, min=min_value)


@given(st.tuples(st.integers(min_value=1), st.integers(max_value=0)))
def test_max_greater_than_zero(pair: tuple[int, int]) -> None:
    """Test that max team size should be > 0."""
    min_value, max_value = pair
    with pytest.raises(InvalidCompetitionDataError, match="Max team size must be greater than 0"):
        TeamSizeRange(max=max_value, min=min_value)


@given(ordered_pairs().filter(lambda pair: pair[0] > 0 and pair[0] != pair[1]))
def test_min_not_exceed_max(pair: tuple[int, int]) -> None:
    """Test that max team size should be >= min team size."""
    max_value, min_value = pair
    with pytest.raises(InvalidCompetitionDataError, match="Min team size must be less than or equal to max team size"):
        TeamSizeRange(max=max_value, min=min_value)
