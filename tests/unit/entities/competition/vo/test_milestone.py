from datetime import datetime

import pytest
from faker import Faker
from hypothesis import given

from dreamteams.entities.competition.milestone import Milestone, MilestoneData, milestone_factory
from dreamteams.entities.errors.competition import InvalidCompetitionDataError
from dreamteams_common.clock import Clock
from tests.unit.composite import dt_past, milestone_data


@given(milestone_data())
def test_create_milestone_with_valid_data(
    clock: Clock,
    data: MilestoneData,
) -> None:
    """Milestone factory returns an entity matching the input data (title, timestamp, optional description)."""
    milestone = milestone_factory(data, clock)

    assert milestone == Milestone(
        timestamp=data.timestamp.replace(second=0, microsecond=0),
        title=data.title,
        description=data.description,
    )


@given(dt_past())
def test_timestamp_must_be_in_future(clock: Clock, faker: Faker, timestamp: datetime) -> None:
    """Test that milestone with timestamp in past raises error."""
    with pytest.raises(InvalidCompetitionDataError, match="Milestone timestamp cannot be in past"):
        milestone_factory(MilestoneData(timestamp=timestamp, title=faker.sentence(nb_words=4)), clock)
