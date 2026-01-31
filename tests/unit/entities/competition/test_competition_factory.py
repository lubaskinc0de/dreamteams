import pytest
from hypothesis import HealthCheck, assume, given, settings

from dreamteams.entities.common.clock import Clock
from dreamteams.entities.competition.entity import Competition, CompetitionData, competition_factory
from dreamteams.entities.competition.milestone import milestone_factory
from dreamteams.entities.competition.schedule import CompetitionSchedule
from dreamteams.entities.errors.competition import InvalidCompetitionDataError
from dreamteams.entities.user import User
from tests.unit.composite import valid_competition_data


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(valid_competition_data())
def test_create_competition_with_valid_data(
    organizer_user: User,
    clock: Clock,
    data: CompetitionData,
) -> None:
    """Test creating competition succeeds."""
    competition = competition_factory(
        user=organizer_user,
        data=data,
        clock=clock,
    )

    assert organizer_user.organizer is not None
    assert competition.created_at == competition.updated_at
    assert competition == Competition(
        id=competition.id,
        organizer_id=organizer_user.organizer.id,
        title=data.title,
        description=data.description,
        schedule=CompetitionSchedule(
            data.schedule.registration_start,
            data.schedule.registration_end,
            data.schedule.team_formation_start,
            data.schedule.team_formation_end,
        ),
        participant_limits=data.participant_limits,
        domains=data.domains,
        participant_type=data.participant_type,
        venue=data.venue,
        team_size=data.team_size,
        banner=None,
        is_archived=True,
        milestones=[milestone_factory(milestone_data, clock) for milestone_data in data.milestones]
        if data.milestones is not None
        else [],
        created_at=competition.created_at,
        updated_at=competition.updated_at,
    )


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(valid_competition_data())
def test_competition_milestones_are_unique(
    organizer_user: User,
    clock: Clock,
    data: CompetitionData,
) -> None:
    """Test cannot create competition with duplicate milestones."""
    assume(data.milestones and len(data.milestones) > 1)
    first_element = data.milestones[0]  # type: ignore[index]
    data.milestones = [first_element for _ in data.milestones]  # type: ignore[union-attr]

    with pytest.raises(InvalidCompetitionDataError, match="Milestone timestamps must be unique"):
        competition_factory(
            user=organizer_user,
            data=data,
            clock=clock,
        )


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(valid_competition_data())
def test_competition_domains_list_is_not_empty(
    organizer_user: User,
    clock: Clock,
    data: CompetitionData,
) -> None:
    """Test cannot create competition with empty domains list."""
    data.domains = []

    with pytest.raises(InvalidCompetitionDataError, match="Domains list must not be empty"):
        competition_factory(
            user=organizer_user,
            data=data,
            clock=clock,
        )


@pytest.mark.parametrize("empty_string", ["", " ", "   "])
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(valid_competition_data())
def test_competition_description_is_not_empty(
    empty_string: str,
    organizer_user: User,
    clock: Clock,
    data: CompetitionData,
) -> None:
    """Test cannot create competition with empty description."""
    data.description = empty_string

    with pytest.raises(InvalidCompetitionDataError, match="Description must not be empty"):
        competition_factory(
            user=organizer_user,
            data=data,
            clock=clock,
        )
