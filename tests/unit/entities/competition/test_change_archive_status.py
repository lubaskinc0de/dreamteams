from copy import deepcopy
from typing import Literal

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from dreamteams.entities.common.clock import Clock
from dreamteams.entities.competition.entity import Competition
from dreamteams.entities.errors.base import AccessDeniedError
from tests.unit.composite import valid_competition
from tests.unit.helpers.facade import Gateway


@settings(max_examples=30)
@given(st.data(), st.booleans())
def test_archive_status_change_succeeds(
    gateway: Gateway,
    clock: Clock,
    data: st.DataObject,
    is_archived: Literal[False, True],
) -> None:
    """Archive status change updates only the archive flag."""
    # Arrange
    organizer = gateway.organizer.create()
    competition = data.draw(valid_competition(organizer, clock))
    before_update = deepcopy(competition)

    # Act
    competition.change_archive_status(is_archived=is_archived, organizer=organizer, clock=clock)

    # Assert
    assert competition == Competition(
        id=competition.id,
        organizer_id=organizer.id,
        organizer=organizer,
        title=before_update.title,
        description=before_update.description,
        schedule=before_update.schedule,
        participant_limits=before_update.participant_limits,
        tags=before_update.tags,
        tracks=before_update.tracks,
        participant_type=before_update.participant_type,
        venue=before_update.venue,
        team_size=before_update.team_size,
        banner=before_update.banner,
        auto_accept=before_update.auto_accept,
        is_archived=is_archived,
        milestones=before_update.milestones,
        created_at=competition.created_at,
        updated_at=competition.updated_at,
    )


@settings(max_examples=30)
@given(st.data(), st.booleans())
def test_only_owner_can_change_archive_status(
    gateway: Gateway,
    clock: Clock,
    data: st.DataObject,
    is_archived: Literal[False, True],
) -> None:
    """Only the owning organizer can change competition archive status."""
    # Arrange
    organizer = gateway.organizer.create()
    different_organizer = gateway.organizer.create()
    competition = data.draw(valid_competition(organizer, clock))

    # Act / Assert
    with pytest.raises(AccessDeniedError):
        competition.change_archive_status(is_archived=is_archived, organizer=different_organizer, clock=clock)
