import pytest
from hypothesis import HealthCheck, assume, given, settings
from hypothesis import strategies as st

from dreamteams.entities.application.entity import (
    Application,
    ApplicationData,
    ApplicationStatus,
    application_factory,
)
from dreamteams.entities.common.clock import Clock
from dreamteams.entities.common.vo.domain import Domain
from dreamteams.entities.errors.application import InvalidApplicationDataError
from dreamteams.entities.errors.base import AccessDeniedError
from dreamteams.entities.user import User
from tests.unit.composite import valid_application_data, valid_competition


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=30)
@given(st.data())
def test_create_application_with_valid_data(
    participant_user: User,
    organizer_user: User,
    clock: Clock,
    data: st.DataObject,
) -> None:
    """Test creating application succeeds with valid data."""
    competition = data.draw(valid_competition(organizer_user, clock))
    app_data = data.draw(valid_application_data(domains=competition.domains))

    application = application_factory(
        data=app_data,
        user=participant_user,
        competition=competition,
        clock=clock,
    )

    assert participant_user.participant is not None
    assert application == Application(
        id=application.id,
        participant_id=participant_user.participant.id,
        competition_id=competition.id,
        domains=app_data.domains,
        status=ApplicationStatus.ACCEPTED if competition.auto_accept else ApplicationStatus.PENDING,
        created_at=application.created_at,
    )


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=30)
@given(st.data())
def test_application_domains_must_not_be_empty(
    participant_user: User,
    organizer_user: User,
    clock: Clock,
    data: st.DataObject,
) -> None:
    """Test cannot create application with empty domains list."""
    competition = data.draw(valid_competition(organizer_user, clock))

    with pytest.raises(InvalidApplicationDataError, match="Domains list must not be empty"):
        application_factory(
            data=ApplicationData(domains=[]),
            user=participant_user,
            competition=competition,
            clock=clock,
        )


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=30)
@given(st.data())
def test_application_domains_must_be_subset_of_competition(
    participant_user: User,
    organizer_user: User,
    clock: Clock,
    data: st.DataObject,
) -> None:
    """Test application domains must be a subset of competition domains."""
    competition = data.draw(valid_competition(organizer_user, clock))

    all_domains = set(Domain)
    extra_domains = all_domains - set(competition.domains)
    assume(len(extra_domains) > 0)

    invalid_domain = data.draw(st.sampled_from(sorted(extra_domains)))

    with pytest.raises(
        InvalidApplicationDataError,
        match="Application domains must be a subset of competition domains",
    ):
        application_factory(
            data=ApplicationData(domains=[invalid_domain]),
            user=participant_user,
            competition=competition,
            clock=clock,
        )


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=30)
@given(st.data())
def test_only_participant_can_apply(
    organizer_user: User,
    clock: Clock,
    data: st.DataObject,
) -> None:
    """Test user without participant role cannot create application."""
    competition = data.draw(valid_competition(organizer_user, clock))
    app_data = data.draw(valid_application_data(domains=competition.domains))

    with pytest.raises(AccessDeniedError, match="Only participants can apply"):
        application_factory(
            data=app_data,
            user=organizer_user,
            competition=competition,
            clock=clock,
        )
