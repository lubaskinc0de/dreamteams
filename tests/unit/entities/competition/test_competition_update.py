import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from dreamteams.entities.common.clock import Clock
from dreamteams.entities.competition.entity import Competition, UpdateCompetitionData
from dreamteams.entities.competition.schedule import CompetitionSchedule
from dreamteams.entities.errors.base import AccessDeniedError
from dreamteams.entities.errors.competition import InvalidCompetitionDataError
from dreamteams.entities.user import User
from tests.unit.composite import milestone, valid_competition, valid_competition_update_data


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(st.data(), valid_competition_update_data())
def test_update_competition_succeeds(
    organizer_user: User,
    clock: Clock,
    data: st.DataObject,
    valid_competition_update_data: UpdateCompetitionData,
) -> None:
    """Test updating competition succeeds."""
    competition = data.draw(valid_competition(organizer_user, clock))

    competition.update(
        valid_competition_update_data,
        organizer_user,
        clock,
    )

    assert organizer_user.organizer is not None
    assert competition == Competition(
        id=competition.id,
        organizer_id=organizer_user.organizer.id,
        title=valid_competition_update_data.title,
        description=valid_competition_update_data.description,
        schedule=CompetitionSchedule(
            valid_competition_update_data.schedule.registration_start,
            valid_competition_update_data.schedule.registration_end,
            valid_competition_update_data.schedule.team_formation_start,
            valid_competition_update_data.schedule.team_formation_end,
        ),
        participant_limits=valid_competition_update_data.participant_limits,
        domains=valid_competition_update_data.domains,
        participant_type=valid_competition_update_data.participant_type,
        venue=valid_competition_update_data.venue,
        team_size=valid_competition_update_data.team_size,
        banner=None,
        is_archived=valid_competition_update_data.is_archived,
        milestones=valid_competition_update_data.milestones
        if valid_competition_update_data.milestones is not None
        else [],
        created_at=competition.created_at,
        updated_at=competition.updated_at,
    )


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(st.data(), valid_competition_update_data())
def test_competition_milestones_are_unique(
    organizer_user: User,
    clock: Clock,
    data: st.DataObject,
    valid_competition_update_data: UpdateCompetitionData,
) -> None:
    """Test cannot create competition with duplicate milestones."""
    competition = data.draw(valid_competition(organizer_user, clock))
    valid_competition_update_data.milestones = [data.draw(milestone())] * 2

    with pytest.raises(InvalidCompetitionDataError, match="Milestone timestamps must be unique"):
        competition.update(
            valid_competition_update_data,
            organizer_user,
            clock,
        )


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(st.data(), valid_competition_update_data())
def test_only_owner_can_update_competition(
    organizer_user: User,
    different_user: User,
    clock: Clock,
    data: st.DataObject,
    valid_competition_update_data: UpdateCompetitionData,
) -> None:
    """Test only owner of this competition can update it."""
    competition = data.draw(valid_competition(organizer_user, clock))

    with pytest.raises(AccessDeniedError):
        competition.update(
            valid_competition_update_data,
            different_user,
            clock,
        )


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(st.data(), valid_competition_update_data())
def test_only_organizer_can_update_competition(
    organizer_user: User,
    user_without_organizer: User,
    clock: Clock,
    data: st.DataObject,
    valid_competition_update_data: UpdateCompetitionData,
) -> None:
    """Test only organizer can update competition."""
    competition = data.draw(valid_competition(organizer_user, clock))

    with pytest.raises(AccessDeniedError):
        competition.update(
            valid_competition_update_data,
            user_without_organizer,
            clock,
        )


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(st.data(), valid_competition_update_data())
def test_competition_domains_are_not_empty(
    organizer_user: User,
    clock: Clock,
    data: st.DataObject,
    valid_competition_update_data: UpdateCompetitionData,
) -> None:
    """Test cannot update competition with empty domains."""
    competition = data.draw(valid_competition(organizer_user, clock))
    valid_competition_update_data.domains = []

    with pytest.raises(InvalidCompetitionDataError, match="Domains list must not be empty"):
        competition.update(
            valid_competition_update_data,
            organizer_user,
            clock,
        )


@pytest.mark.parametrize("empty_string", ["", " ", "   "])
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(st.data(), valid_competition_update_data())
def test_competition_descriptions_are_not_empty(
    empty_string: str,
    organizer_user: User,
    clock: Clock,
    data: st.DataObject,
    valid_competition_update_data: UpdateCompetitionData,
) -> None:
    """Test cannot update competition with empty description."""
    competition = data.draw(valid_competition(organizer_user, clock))
    valid_competition_update_data.description = empty_string

    with pytest.raises(InvalidCompetitionDataError, match="Description must not be empty"):
        competition.update(
            valid_competition_update_data,
            organizer_user,
            clock,
        )
