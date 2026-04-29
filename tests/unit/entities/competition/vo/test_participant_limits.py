import pytest
from hypothesis import given
from hypothesis import strategies as st

from dreamteams.entities.competition.participant_limits import ParticipantLimits
from dreamteams.entities.errors.competition import InvalidCompetitionDataError


@given(st.integers(min_value=1))
def test_create_with_valid_values(max_value: int) -> None:
    """Test creating ParticipantLimits with a valid max value."""
    limits = ParticipantLimits(max=max_value)

    assert limits.max == max_value


@given(st.integers(max_value=0))
def test_max_greater_than_zero(max_value: int) -> None:
    """Test that max value must be > 0."""
    with pytest.raises(InvalidCompetitionDataError, match="Max participants must be greater than 0"):
        ParticipantLimits(max=max_value)
