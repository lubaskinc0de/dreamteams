from typing import Any

import pytest
from hypothesis import HealthCheck, assume, given, settings
from hypothesis import strategies as st

from dreamteams.entities.application.entity import Application, ApplicationData, ApplicationStatus
from dreamteams.entities.application.submit_service import submit_application
from dreamteams.entities.application_form.entity import ApplicationForm, ApplicationFormData, application_form_factory
from dreamteams.entities.application_form.vo.field import Field, FieldChoice, FieldType
from dreamteams.entities.common.clock import Clock
from dreamteams.entities.common.vo.domain import Domain
from dreamteams.entities.common.vo.participant_type import ParticipantType
from dreamteams.entities.competition.participant_limits import ParticipantLimits
from dreamteams.entities.errors.application import (
    CompetitionNotActiveError,
    InvalidApplicationDataError,
    ParticipantLimitsExceededError,
    ParticipantTypeMismatchError,
)
from dreamteams.entities.errors.base import AccessDeniedError
from dreamteams.entities.user import User
from tests.unit.composite import (
    valid_application_data,
    valid_application_form_data,
    valid_competition,
    valid_form_data_for_form,
)

_CHOICES = (FieldChoice(value="S", label="Small"), FieldChoice(value="M", label="Medium"))
_MULTI_CHOICES = (FieldChoice(value="fe", label="Frontend"), FieldChoice(value="be", label="Backend"))


def _make_form(
    organizer_user: User,
    competition: Any,
    clock: Clock,
    *fields: Field,
) -> ApplicationForm:
    return application_form_factory(
        data=ApplicationFormData(fields=list(fields)),
        competition=competition,
        user=organizer_user,
        clock=clock,
    )


# --- Happy path ---


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=30)
@given(st.data())
def test_application_is_created_with_valid_data(
    participant_user: User,
    organizer_user: User,
    clock: Clock,
    data: st.DataObject,
) -> None:
    """Valid submission to an open competition creates a correctly formed Application."""
    competition = data.draw(valid_competition(organizer_user, clock, is_archived=False, is_open=True))
    competition.participant_type = ParticipantType.ANY
    competition.participant_limits = ParticipantLimits(max=1000, min=1)
    app_data = data.draw(valid_application_data(domains=competition.domains))

    application = submit_application(
        data=app_data,
        user=participant_user,
        competition=competition,
        accepted_count=0,
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
        form_data=app_data.form_data,
    )


# --- Archived / registration window ---


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=30)
@given(st.data())
def test_archived_competition_is_rejected(
    participant_user: User,
    organizer_user: User,
    clock: Clock,
    data: st.DataObject,
) -> None:
    """Submitting to an archived competition raises CompetitionNotActiveError regardless of schedule."""
    competition = data.draw(valid_competition(organizer_user, clock, is_archived=True, is_open=True))
    app_data = data.draw(valid_application_data(domains=competition.domains))

    with pytest.raises(CompetitionNotActiveError):
        submit_application(
            data=app_data,
            user=participant_user,
            competition=competition,
            accepted_count=0,
            clock=clock,
        )


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=30)
@given(st.data())
def test_registration_not_yet_started_is_rejected(
    participant_user: User,
    organizer_user: User,
    clock: Clock,
    data: st.DataObject,
) -> None:
    """Submitting before registration opens raises CompetitionNotActiveError."""
    # is_open=False (default) → factory-generated future schedule, registration not yet started
    competition = data.draw(valid_competition(organizer_user, clock, is_archived=False))
    app_data = data.draw(valid_application_data(domains=competition.domains))

    with pytest.raises(CompetitionNotActiveError):
        submit_application(
            data=app_data,
            user=participant_user,
            competition=competition,
            accepted_count=0,
            clock=clock,
        )


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=30)
@given(st.data())
def test_registration_already_ended_is_rejected(
    participant_user: User,
    organizer_user: User,
    clock: Clock,
    data: st.DataObject,
) -> None:
    """Submitting after registration closes raises CompetitionNotActiveError."""
    competition = data.draw(valid_competition(organizer_user, clock, is_archived=False, is_ended=True))
    app_data = data.draw(valid_application_data(domains=competition.domains))

    with pytest.raises(CompetitionNotActiveError):
        submit_application(
            data=app_data,
            user=participant_user,
            competition=competition,
            accepted_count=0,
            clock=clock,
        )


# --- Participant type ---


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=30)
@given(st.data())
def test_participant_type_mismatch_is_rejected(
    participant_user: User,
    organizer_user: User,
    clock: Clock,
    data: st.DataObject,
) -> None:
    """SCHOOLCHILD competition rejects a STUDENT participant with ParticipantTypeMismatchError."""
    assert participant_user.participant is not None
    assert participant_user.participant.participant_type == ParticipantType.STUDENT
    competition = data.draw(valid_competition(organizer_user, clock, is_archived=False, is_open=True))
    competition.participant_type = ParticipantType.SCHOOLCHILD
    app_data = data.draw(valid_application_data(domains=competition.domains))

    with pytest.raises(ParticipantTypeMismatchError):
        submit_application(
            data=app_data,
            user=participant_user,
            competition=competition,
            accepted_count=0,
            clock=clock,
        )


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=30)
@given(st.data())
def test_participant_type_any_accepts_any_participant(
    participant_user: User,
    organizer_user: User,
    clock: Clock,
    data: st.DataObject,
) -> None:
    """A competition with participant_type=ANY accepts participants of any type."""
    competition = data.draw(valid_competition(organizer_user, clock, is_archived=False, is_open=True))
    competition.participant_type = ParticipantType.ANY
    competition.participant_limits = ParticipantLimits(max=1000, min=1)
    app_data = data.draw(valid_application_data(domains=competition.domains))

    application = submit_application(
        data=app_data,
        user=participant_user,
        competition=competition,
        accepted_count=0,
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
        form_data=app_data.form_data,
    )


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=30)
@given(st.data())
def test_matching_participant_type_is_accepted(
    participant_user: User,
    organizer_user: User,
    clock: Clock,
    data: st.DataObject,
) -> None:
    """STUDENT competition accepts a STUDENT participant."""
    assert participant_user.participant is not None
    assert participant_user.participant.participant_type == ParticipantType.STUDENT
    competition = data.draw(valid_competition(organizer_user, clock, is_archived=False, is_open=True))
    competition.participant_type = ParticipantType.STUDENT
    competition.participant_limits = ParticipantLimits(max=1000, min=1)
    app_data = data.draw(valid_application_data(domains=competition.domains))

    application = submit_application(
        data=app_data,
        user=participant_user,
        competition=competition,
        accepted_count=0,
        clock=clock,
    )

    assert application == Application(
        id=application.id,
        participant_id=participant_user.participant.id,
        competition_id=competition.id,
        domains=app_data.domains,
        status=ApplicationStatus.ACCEPTED if competition.auto_accept else ApplicationStatus.PENDING,
        created_at=application.created_at,
        form_data=app_data.form_data,
    )


# --- Participant limits ---


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=30)
@given(st.data())
def test_participant_limits_exceeded_is_rejected(
    participant_user: User,
    organizer_user: User,
    clock: Clock,
    data: st.DataObject,
) -> None:
    """accepted_count >= max raises ParticipantLimitsExceededError (covers both at-max and above-max)."""
    max_participants = data.draw(st.integers(min_value=1, max_value=100))
    accepted_count = data.draw(st.integers(min_value=max_participants))
    competition = data.draw(valid_competition(organizer_user, clock, is_archived=False, is_open=True))
    competition.participant_type = ParticipantType.ANY
    competition.participant_limits = ParticipantLimits(max=max_participants, min=1)
    app_data = data.draw(valid_application_data(domains=competition.domains))

    with pytest.raises(ParticipantLimitsExceededError):
        submit_application(
            data=app_data,
            user=participant_user,
            competition=competition,
            accepted_count=accepted_count,
            clock=clock,
        )


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=30)
@given(st.data())
def test_accepted_count_below_max_is_accepted(
    participant_user: User,
    organizer_user: User,
    clock: Clock,
    data: st.DataObject,
) -> None:
    """accepted_count strictly below max allows the application through."""
    max_participants = data.draw(st.integers(min_value=2, max_value=100))
    accepted_count = data.draw(st.integers(min_value=0, max_value=max_participants - 1))
    competition = data.draw(valid_competition(organizer_user, clock, is_archived=False, is_open=True))
    competition.participant_type = ParticipantType.ANY
    competition.participant_limits = ParticipantLimits(max=max_participants, min=1)
    app_data = data.draw(valid_application_data(domains=competition.domains))

    application = submit_application(
        data=app_data,
        user=participant_user,
        competition=competition,
        accepted_count=accepted_count,
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
        form_data=app_data.form_data,
    )


# --- auto_accept status ---


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=30)
@given(st.data())
def test_auto_accept_competition_produces_accepted_status(
    participant_user: User,
    organizer_user: User,
    clock: Clock,
    data: st.DataObject,
) -> None:
    """Application submitted to auto_accept=True competition receives ACCEPTED status."""
    competition = data.draw(valid_competition(organizer_user, clock, is_archived=False, is_open=True))
    competition.participant_type = ParticipantType.ANY
    competition.participant_limits = ParticipantLimits(max=1000, min=1)
    competition.auto_accept = True
    app_data = data.draw(valid_application_data(domains=competition.domains))

    application = submit_application(
        data=app_data,
        user=participant_user,
        competition=competition,
        accepted_count=0,
        clock=clock,
    )

    assert participant_user.participant is not None
    assert application == Application(
        id=application.id,
        participant_id=participant_user.participant.id,
        competition_id=competition.id,
        domains=app_data.domains,
        status=ApplicationStatus.ACCEPTED,
        created_at=application.created_at,
        form_data=app_data.form_data,
    )


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=30)
@given(st.data())
def test_non_auto_accept_competition_produces_pending_status(
    participant_user: User,
    organizer_user: User,
    clock: Clock,
    data: st.DataObject,
) -> None:
    """Application submitted to auto_accept=False competition receives PENDING status."""
    competition = data.draw(valid_competition(organizer_user, clock, is_archived=False, is_open=True))
    competition.participant_type = ParticipantType.ANY
    competition.participant_limits = ParticipantLimits(max=1000, min=1)
    competition.auto_accept = False
    app_data = data.draw(valid_application_data(domains=competition.domains))

    application = submit_application(
        data=app_data,
        user=participant_user,
        competition=competition,
        accepted_count=0,
        clock=clock,
    )

    assert participant_user.participant is not None
    assert application == Application(
        id=application.id,
        participant_id=participant_user.participant.id,
        competition_id=competition.id,
        domains=app_data.domains,
        status=ApplicationStatus.PENDING,
        created_at=application.created_at,
        form_data=app_data.form_data,
    )


# --- Domain validation ---


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=30)
@given(st.data())
def test_empty_domains_are_rejected(
    participant_user: User,
    organizer_user: User,
    clock: Clock,
    data: st.DataObject,
) -> None:
    """Submitting with an empty domains list raises InvalidApplicationDataError."""
    competition = data.draw(valid_competition(organizer_user, clock, is_archived=False, is_open=True))
    competition.participant_type = ParticipantType.ANY
    competition.participant_limits = ParticipantLimits(max=1000, min=1)

    with pytest.raises(InvalidApplicationDataError, match="Domains list must not be empty"):
        submit_application(
            data=ApplicationData(domains=[]),
            user=participant_user,
            competition=competition,
            accepted_count=0,
            clock=clock,
        )


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=30)
@given(st.data())
def test_domains_outside_competition_are_rejected(
    participant_user: User,
    organizer_user: User,
    clock: Clock,
    data: st.DataObject,
) -> None:
    """Application domains must be a subset of the competition's domains."""
    competition = data.draw(valid_competition(organizer_user, clock, is_archived=False, is_open=True))
    competition.participant_type = ParticipantType.ANY
    competition.participant_limits = ParticipantLimits(max=1000, min=1)
    all_domains = set(Domain)
    extra_domains = all_domains - set(competition.domains)
    assume(len(extra_domains) > 0)
    invalid_domain = data.draw(st.sampled_from(sorted(extra_domains)))

    with pytest.raises(
        InvalidApplicationDataError,
        match="Application domains must be a subset of competition domains",
    ):
        submit_application(
            data=ApplicationData(domains=[invalid_domain]),
            user=participant_user,
            competition=competition,
            accepted_count=0,
            clock=clock,
        )


# --- Access control ---


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=30)
@given(st.data())
def test_non_participant_user_is_rejected(
    organizer_user: User,
    clock: Clock,
    data: st.DataObject,
) -> None:
    """User without a participant role cannot submit an application."""
    assert organizer_user.participant is None
    competition = data.draw(valid_competition(organizer_user, clock, is_archived=False, is_open=True))
    competition.participant_type = ParticipantType.ANY
    competition.participant_limits = ParticipantLimits(max=1000, min=1)
    app_data = data.draw(valid_application_data(domains=competition.domains))

    with pytest.raises(AccessDeniedError, match="Only participants can apply"):
        submit_application(
            data=app_data,
            user=organizer_user,
            competition=competition,
            accepted_count=0,
            clock=clock,
        )


# --- form_data validation ---


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=30)
@given(st.data())
def test_null_form_data_accepted_when_no_form(
    participant_user: User,
    organizer_user: User,
    clock: Clock,
    data: st.DataObject,
) -> None:
    """form_data=None is accepted when the competition has no ApplicationForm."""
    competition = data.draw(valid_competition(organizer_user, clock, is_archived=False, is_open=True))
    competition.participant_type = ParticipantType.ANY
    competition.participant_limits = ParticipantLimits(max=1000, min=1)
    app_data = data.draw(valid_application_data(domains=competition.domains))
    app_data.form_data = None

    application = submit_application(
        data=app_data,
        user=participant_user,
        competition=competition,
        accepted_count=0,
        clock=clock,
    )

    assert application.form_data is None


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=30)
@given(st.data())
def test_form_data_rejected_when_no_form_exists(
    participant_user: User,
    organizer_user: User,
    clock: Clock,
    data: st.DataObject,
) -> None:
    """Non-null form_data is rejected when the competition has no ApplicationForm."""
    competition = data.draw(valid_competition(organizer_user, clock, is_archived=False, is_open=True))
    competition.participant_type = ParticipantType.ANY
    competition.participant_limits = ParticipantLimits(max=1000, min=1)
    app_data = data.draw(valid_application_data(domains=competition.domains))
    app_data.form_data = {"unexpected": "value"}

    with pytest.raises(InvalidApplicationDataError, match="form_data must be None"):
        submit_application(
            data=app_data,
            user=participant_user,
            competition=competition,
            accepted_count=0,
            clock=clock,
        )


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=30)
@given(st.data())
def test_valid_form_data_is_accepted(
    participant_user: User,
    organizer_user: User,
    clock: Clock,
    data: st.DataObject,
) -> None:
    """Valid answers matching the ApplicationForm are accepted and stored on the application."""
    competition = data.draw(valid_competition(organizer_user, clock, is_archived=False, is_open=True))
    competition.participant_type = ParticipantType.ANY
    competition.participant_limits = ParticipantLimits(max=1000, min=1)
    form_input = data.draw(valid_application_form_data())
    form = application_form_factory(data=form_input, competition=competition, user=organizer_user, clock=clock)
    answers = data.draw(valid_form_data_for_form(form))
    app_data = data.draw(valid_application_data(domains=competition.domains))
    app_data.form_data = answers

    application = submit_application(
        data=app_data,
        user=participant_user,
        competition=competition,
        accepted_count=0,
        clock=clock,
        form=form,
    )

    assert application.form_data == answers


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=30)
@given(st.data())
def test_missing_required_field_is_rejected(
    participant_user: User,
    organizer_user: User,
    clock: Clock,
    data: st.DataObject,
) -> None:
    """Omitting a required form field raises InvalidApplicationDataError."""
    competition = data.draw(valid_competition(organizer_user, clock, is_archived=False, is_open=True))
    competition.participant_type = ParticipantType.ANY
    competition.participant_limits = ParticipantLimits(max=1000, min=1)
    form = _make_form(organizer_user, competition, clock, Field(name="bio", label="Bio", type=FieldType.STRING))
    app_data = data.draw(valid_application_data(domains=competition.domains))
    app_data.form_data = {}

    with pytest.raises(InvalidApplicationDataError, match="Required field 'bio' is missing"):
        submit_application(
            data=app_data,
            user=participant_user,
            competition=competition,
            accepted_count=0,
            clock=clock,
            form=form,
        )


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=30)
@given(st.data())
def test_optional_field_can_be_omitted(
    participant_user: User,
    organizer_user: User,
    clock: Clock,
    data: st.DataObject,
) -> None:
    """Omitting an optional form field does not raise an error."""
    competition = data.draw(valid_competition(organizer_user, clock, is_archived=False, is_open=True))
    competition.participant_type = ParticipantType.ANY
    competition.participant_limits = ParticipantLimits(max=1000, min=1)
    form = _make_form(
        organizer_user,
        competition,
        clock,
        Field(name="bio", label="Bio", type=FieldType.STRING, required=True),
        Field(name="age", label="Age", type=FieldType.INT, required=False),
    )
    app_data = data.draw(valid_application_data(domains=competition.domains))
    app_data.form_data = {"bio": "hello"}

    application = submit_application(
        data=app_data,
        user=participant_user,
        competition=competition,
        accepted_count=0,
        clock=clock,
        form=form,
    )

    assert application.form_data == {"bio": "hello"}


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=30)
@given(st.data())
def test_extra_form_key_is_rejected(
    participant_user: User,
    organizer_user: User,
    clock: Clock,
    data: st.DataObject,
) -> None:
    """Unknown keys in form_data raise InvalidApplicationDataError."""
    competition = data.draw(valid_competition(organizer_user, clock, is_archived=False, is_open=True))
    competition.participant_type = ParticipantType.ANY
    competition.participant_limits = ParticipantLimits(max=1000, min=1)
    form = _make_form(organizer_user, competition, clock, Field(name="bio", label="Bio", type=FieldType.STRING))
    app_data = data.draw(valid_application_data(domains=competition.domains))
    app_data.form_data = {"bio": "hi", "ghost": "x"}

    with pytest.raises(InvalidApplicationDataError, match="Unknown form fields"):
        submit_application(
            data=app_data,
            user=participant_user,
            competition=competition,
            accepted_count=0,
            clock=clock,
            form=form,
        )


@pytest.mark.parametrize("bad_value", [42, True, None, []])
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=30)
@given(st.data())
def test_string_field_rejects_non_string_value(
    bad_value: Any,
    participant_user: User,
    organizer_user: User,
    clock: Clock,
    data: st.DataObject,
) -> None:
    """A non-string value for a STRING field raises InvalidApplicationDataError."""
    competition = data.draw(valid_competition(organizer_user, clock, is_archived=False, is_open=True))
    competition.participant_type = ParticipantType.ANY
    competition.participant_limits = ParticipantLimits(max=1000, min=1)
    form = _make_form(organizer_user, competition, clock, Field(name="bio", label="Bio", type=FieldType.STRING))
    app_data = data.draw(valid_application_data(domains=competition.domains))
    app_data.form_data = {"bio": bad_value}

    with pytest.raises(InvalidApplicationDataError, match="must be a string"):
        submit_application(
            data=app_data,
            user=participant_user,
            competition=competition,
            accepted_count=0,
            clock=clock,
            form=form,
        )


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=30)
@given(st.data())
def test_int_field_rejects_bool_value(
    participant_user: User,
    organizer_user: User,
    clock: Clock,
    data: st.DataObject,
) -> None:
    """A bool value for an INT field raises InvalidApplicationDataError."""
    competition = data.draw(valid_competition(organizer_user, clock, is_archived=False, is_open=True))
    competition.participant_type = ParticipantType.ANY
    competition.participant_limits = ParticipantLimits(max=1000, min=1)
    form = _make_form(organizer_user, competition, clock, Field(name="age", label="Age", type=FieldType.INT))
    app_data = data.draw(valid_application_data(domains=competition.domains))
    app_data.form_data = {"age": True}

    with pytest.raises(InvalidApplicationDataError, match="must be an integer"):
        submit_application(
            data=app_data,
            user=participant_user,
            competition=competition,
            accepted_count=0,
            clock=clock,
            form=form,
        )


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=30)
@given(st.data())
def test_select_field_rejects_unknown_choice(
    participant_user: User,
    organizer_user: User,
    clock: Clock,
    data: st.DataObject,
) -> None:
    """A value not in the SELECT field's choices raises InvalidApplicationDataError."""
    competition = data.draw(valid_competition(organizer_user, clock, is_archived=False, is_open=True))
    competition.participant_type = ParticipantType.ANY
    competition.participant_limits = ParticipantLimits(max=1000, min=1)
    form = _make_form(
        organizer_user,
        competition,
        clock,
        Field(name="size", label="Size", type=FieldType.SELECT, choices=_CHOICES),
    )
    app_data = data.draw(valid_application_data(domains=competition.domains))
    app_data.form_data = {"size": "XL"}

    with pytest.raises(InvalidApplicationDataError, match="must be one of"):
        submit_application(
            data=app_data,
            user=participant_user,
            competition=competition,
            accepted_count=0,
            clock=clock,
            form=form,
        )


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=30)
@given(st.data())
def test_multiselect_field_rejects_empty_list(
    participant_user: User,
    organizer_user: User,
    clock: Clock,
    data: st.DataObject,
) -> None:
    """An empty list for a MULTISELECT field raises InvalidApplicationDataError."""
    competition = data.draw(valid_competition(organizer_user, clock, is_archived=False, is_open=True))
    competition.participant_type = ParticipantType.ANY
    competition.participant_limits = ParticipantLimits(max=1000, min=1)
    form = _make_form(
        organizer_user,
        competition,
        clock,
        Field(name="roles", label="Roles", type=FieldType.MULTISELECT, choices=_MULTI_CHOICES),
    )
    app_data = data.draw(valid_application_data(domains=competition.domains))
    app_data.form_data = {"roles": []}

    with pytest.raises(InvalidApplicationDataError, match="must be a non-empty list"):
        submit_application(
            data=app_data,
            user=participant_user,
            competition=competition,
            accepted_count=0,
            clock=clock,
            form=form,
        )


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=30)
@given(st.data())
def test_multiselect_field_rejects_invalid_item(
    participant_user: User,
    organizer_user: User,
    clock: Clock,
    data: st.DataObject,
) -> None:
    """A list item not in MULTISELECT choices raises InvalidApplicationDataError."""
    competition = data.draw(valid_competition(organizer_user, clock, is_archived=False, is_open=True))
    competition.participant_type = ParticipantType.ANY
    competition.participant_limits = ParticipantLimits(max=1000, min=1)
    form = _make_form(
        organizer_user,
        competition,
        clock,
        Field(name="roles", label="Roles", type=FieldType.MULTISELECT, choices=_MULTI_CHOICES),
    )
    app_data = data.draw(valid_application_data(domains=competition.domains))
    app_data.form_data = {"roles": ["fe", "unknown"]}

    with pytest.raises(InvalidApplicationDataError, match="invalid values"):
        submit_application(
            data=app_data,
            user=participant_user,
            competition=competition,
            accepted_count=0,
            clock=clock,
            form=form,
        )
