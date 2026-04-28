import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from dreamteams.entities.competition.entity import Competition, UpdateCompetitionGeneralInfoData
from dreamteams.entities.competition.vo.milestones import CompetitionMilestones
from dreamteams.entities.errors.base import AccessDeniedError
from dreamteams_common.clock import Clock
from tests.unit.composite import (
    valid_competition,
    valid_competition_general_info_data,
)
from tests.unit.helpers.facade import Gateway


@settings(max_examples=30)
@given(st.data(), valid_competition_general_info_data())
def test_general_info_update_succeeds(
    gateway: Gateway,
    clock: Clock,
    data: st.DataObject,
    valid_competition_general_info_data: UpdateCompetitionGeneralInfoData,
) -> None:
    """General information update changes editable details and preserves schedule/archive state."""
    # Arrange
    organizer = gateway.organizer.create()
    competition = data.draw(valid_competition(organizer, clock))
    current_schedule = competition.schedule
    current_team_size = competition.team_size
    current_is_archived = competition.is_archived

    # Act
    competition.update_general_info(
        valid_competition_general_info_data,
        organizer,
        clock,
    )

    # Assert
    assert competition == Competition(
        id=competition.id,
        organizer_id=organizer.id,
        organizer=organizer,
        title=valid_competition_general_info_data.title,
        description=valid_competition_general_info_data.description,
        schedule=current_schedule,
        participant_limits=valid_competition_general_info_data.participant_limits,
        tags=valid_competition_general_info_data.tags,
        tracks=valid_competition_general_info_data.tracks,
        participant_type=valid_competition_general_info_data.participant_type,
        venue=valid_competition_general_info_data.venue,
        team_size=current_team_size,
        banner=None,
        auto_accept=valid_competition_general_info_data.auto_accept,
        is_archived=current_is_archived,
        milestones=valid_competition_general_info_data.milestones
        if valid_competition_general_info_data.milestones is not None
        else CompetitionMilestones(),
        created_at=competition.created_at,
        updated_at=competition.updated_at,
    )


@settings(max_examples=30)
@given(st.data(), valid_competition_general_info_data())
def test_only_owner_can_update_general_info(
    gateway: Gateway,
    clock: Clock,
    data: st.DataObject,
    valid_competition_general_info_data: UpdateCompetitionGeneralInfoData,
) -> None:
    """Only the owning organizer can update competition general information."""
    # Arrange
    organizer = gateway.organizer.create()
    different_organizer = gateway.organizer.create()
    competition = data.draw(valid_competition(organizer, clock))

    # Act / Assert
    with pytest.raises(AccessDeniedError):
        competition.update_general_info(
            valid_competition_general_info_data,
            different_organizer,
            clock,
        )
