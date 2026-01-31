import pytest
from hypothesis import given
from hypothesis import strategies as st

from dreamteams.entities.competition.participant_limits import ParticipantLimits
from dreamteams.entities.errors.competition import InvalidCompetitionDataError
from tests.unit.composite import ordered_pairs


@given(ordered_pairs().filter(lambda pair: pair[0] > 0 and pair[1] > 0))
def test_create_with_valid_values(pair: tuple[int, int]) -> None:
    """Test creating ParticipantLimits with valid values."""
    min_value, max_value = pair
    limits = ParticipantLimits(max=max_value, min=min_value)

    assert limits.max == max_value
    assert limits.min == min_value


@given(st.tuples(st.integers(min_value=1), st.integers(max_value=0)))
def test_max_greater_than_zero(pair: tuple[int, int]) -> None:
    """Test that max value must be > 0."""
    min_value, max_value = pair
    with pytest.raises(InvalidCompetitionDataError, match="Max participants must be greater than 0"):
        ParticipantLimits(max=max_value, min=min_value)


@given(ordered_pairs().filter(lambda pair: pair[0] <= 0 and pair[1] > 0))
def test_min_greater_than_zero(pair: tuple[int, int]) -> None:
    """Test that min value must be > 0."""
    min_value, max_value = pair
    with pytest.raises(InvalidCompetitionDataError, match="Min participants must be greater than 0"):
        ParticipantLimits(max=max_value, min=min_value)


@given(ordered_pairs().filter(lambda pair: pair[0] > 0 and pair[0] != pair[1]))
def test_min_not_exceed_max(pair: tuple[int, int]) -> None:
    """Test that min value <= max value."""
    max_value, min_value = pair
    with pytest.raises(
        InvalidCompetitionDataError,
        match="Min participants must be less than or equal to max participants",
    ):
        ParticipantLimits(max=max_value, min=min_value)
