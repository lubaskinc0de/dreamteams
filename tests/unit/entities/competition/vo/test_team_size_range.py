import pytest
from hypothesis import given
from hypothesis import strategies as st

from dreamteams.entities.competition.team_size_range import TeamSizeRange
from dreamteams.entities.errors.competition import InvalidCompetitionDataError
from tests.unit.composite import ordered_pairs

TEST_TEAM_SIZE_MAX = 1_000

valid_team_size_pairs = st.integers(min_value=1, max_value=TEST_TEAM_SIZE_MAX).flatmap(
    lambda min_value: st.tuples(st.just(min_value), st.integers(min_value=min_value, max_value=TEST_TEAM_SIZE_MAX)),
)

invalid_ordered_team_size_pairs = st.integers(min_value=1, max_value=TEST_TEAM_SIZE_MAX - 1).flatmap(
    lambda max_value: st.tuples(st.just(max_value), st.integers(min_value=max_value + 1, max_value=TEST_TEAM_SIZE_MAX)),
)


@given(valid_team_size_pairs)
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


@given(invalid_ordered_team_size_pairs)
def test_min_not_exceed_max(pair: tuple[int, int]) -> None:
    """Test that max team size should be >= min team size."""
    max_value, min_value = pair
    with pytest.raises(InvalidCompetitionDataError, match="Min team size must be less than or equal to max team size"):
        TeamSizeRange(max=max_value, min=min_value)
