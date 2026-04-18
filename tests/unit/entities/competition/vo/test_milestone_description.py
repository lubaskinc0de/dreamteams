import pytest
from hypothesis import given
from hypothesis import strategies as st

from dreamteams.entities.competition.milestone_description import MilestoneDescription
from dreamteams.entities.errors.competition import InvalidCompetitionDataError


def test_empty_value_is_accepted() -> None:
    """Empty string is a valid description."""
    assert MilestoneDescription("").value == ""


@given(st.text(max_size=MilestoneDescription.MAX_LENGTH))
def test_value_within_max_length_is_accepted(value: str) -> None:
    """Any text at or below the max length is accepted verbatim (includes the boundary)."""
    assert MilestoneDescription(value).value == value


@given(st.text(min_size=MilestoneDescription.MAX_LENGTH + 1, max_size=MilestoneDescription.MAX_LENGTH + 50))
def test_value_over_max_length_raises(value: str) -> None:
    """Inputs over the max length are rejected."""
    with pytest.raises(InvalidCompetitionDataError, match="at most 300 characters"):
        MilestoneDescription(value)
