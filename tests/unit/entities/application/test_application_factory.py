from typing import Any

import pytest
from hypothesis import HealthCheck, assume, given, settings
from hypothesis import strategies as st

from dreamteams.entities.application.entity import (
    Application,
    ApplicationData,
    ApplicationStatus,
    application_factory,
)
from dreamteams.entities.application_form.entity import ApplicationForm, ApplicationFormData, application_form_factory
from dreamteams.entities.application_form.vo.field import Field, FieldChoice, FieldType
from dreamteams.entities.common.clock import Clock
from dreamteams.entities.common.vo.domain import Domain
from dreamteams.entities.errors.application import InvalidApplicationDataError
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


def _make_form(organizer_user: User, competition: Any, clock: Clock, *fields: Field) -> ApplicationForm:
    return application_form_factory(
        data=ApplicationFormData(fields=list(fields)),
        competition=competition,
        user=organizer_user,
        clock=clock,
    )


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


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=30)
@given(st.data())
def test_null_form_data_accepted_when_no_form(
    participant_user: User,
    organizer_user: User,
    clock: Clock,
    data: st.DataObject,
) -> None:
    """form_data=None is accepted when the competition has no ApplicationForm."""
    competition = data.draw(valid_competition(organizer_user, clock))
    app_data = data.draw(valid_application_data(domains=competition.domains))
    app_data.form_data = None

    application = application_factory(data=app_data, user=participant_user, competition=competition, clock=clock)

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
    competition = data.draw(valid_competition(organizer_user, clock))
    app_data = data.draw(valid_application_data(domains=competition.domains))
    app_data.form_data = {"unexpected": "value"}

    with pytest.raises(InvalidApplicationDataError, match="form_data must be None"):
        application_factory(data=app_data, user=participant_user, competition=competition, clock=clock)


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=30)
@given(st.data())
def test_valid_form_data_accepted(
    participant_user: User,
    organizer_user: User,
    clock: Clock,
    data: st.DataObject,
) -> None:
    """Valid answers matching the ApplicationForm are accepted and stored on the application."""
    competition = data.draw(valid_competition(organizer_user, clock))
    form_input = data.draw(valid_application_form_data())
    form = application_form_factory(data=form_input, competition=competition, user=organizer_user, clock=clock)
    answers = data.draw(valid_form_data_for_form(form))
    app_data = data.draw(valid_application_data(domains=competition.domains))
    app_data.form_data = answers

    application = application_factory(
        data=app_data,
        user=participant_user,
        competition=competition,
        clock=clock,
        form=form,
    )

    assert application.form_data == answers


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=30)
@given(st.data())
def test_missing_required_field_rejected(
    participant_user: User,
    organizer_user: User,
    clock: Clock,
    data: st.DataObject,
) -> None:
    """Omitting a required form field raises InvalidApplicationDataError."""
    competition = data.draw(valid_competition(organizer_user, clock))
    form = _make_form(organizer_user, competition, clock, Field(name="bio", label="Bio", type=FieldType.STRING))
    app_data = data.draw(valid_application_data(domains=competition.domains))
    app_data.form_data = {}

    with pytest.raises(InvalidApplicationDataError, match="Required field 'bio' is missing"):
        application_factory(data=app_data, user=participant_user, competition=competition, clock=clock, form=form)


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=30)
@given(st.data())
def test_optional_field_can_be_omitted(
    participant_user: User,
    organizer_user: User,
    clock: Clock,
    data: st.DataObject,
) -> None:
    """Omitting an optional form field does not raise an error."""
    competition = data.draw(valid_competition(organizer_user, clock))
    form = _make_form(
        organizer_user,
        competition,
        clock,
        Field(name="bio", label="Bio", type=FieldType.STRING, required=True),
        Field(name="age", label="Age", type=FieldType.INT, required=False),
    )
    app_data = data.draw(valid_application_data(domains=competition.domains))
    app_data.form_data = {"bio": "hello"}

    application = application_factory(
        data=app_data,
        user=participant_user,
        competition=competition,
        clock=clock,
        form=form,
    )

    assert application.form_data == {"bio": "hello"}


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=30)
@given(st.data())
def test_extra_key_rejected(
    participant_user: User,
    organizer_user: User,
    clock: Clock,
    data: st.DataObject,
) -> None:
    """Unknown keys in form_data raise InvalidApplicationDataError."""
    competition = data.draw(valid_competition(organizer_user, clock))
    form = _make_form(organizer_user, competition, clock, Field(name="bio", label="Bio", type=FieldType.STRING))
    app_data = data.draw(valid_application_data(domains=competition.domains))
    app_data.form_data = {"bio": "hi", "ghost": "x"}

    with pytest.raises(InvalidApplicationDataError, match="Unknown form fields"):
        application_factory(data=app_data, user=participant_user, competition=competition, clock=clock, form=form)


@pytest.mark.parametrize("bad_value", [42, True, None, []])
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=30)
@given(st.data())
def test_string_field_rejects_non_string(
    bad_value: Any,
    participant_user: User,
    organizer_user: User,
    clock: Clock,
    data: st.DataObject,
) -> None:
    """A non-string value for a STRING field raises InvalidApplicationDataError."""
    competition = data.draw(valid_competition(organizer_user, clock))
    form = _make_form(organizer_user, competition, clock, Field(name="bio", label="Bio", type=FieldType.STRING))
    app_data = data.draw(valid_application_data(domains=competition.domains))
    app_data.form_data = {"bio": bad_value}

    with pytest.raises(InvalidApplicationDataError, match="must be a string"):
        application_factory(data=app_data, user=participant_user, competition=competition, clock=clock, form=form)


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=30)
@given(st.data())
def test_int_field_rejects_bool(
    participant_user: User,
    organizer_user: User,
    clock: Clock,
    data: st.DataObject,
) -> None:
    """A bool value for an INT field raises InvalidApplicationDataError."""
    competition = data.draw(valid_competition(organizer_user, clock))
    form = _make_form(organizer_user, competition, clock, Field(name="age", label="Age", type=FieldType.INT))
    app_data = data.draw(valid_application_data(domains=competition.domains))
    app_data.form_data = {"age": True}

    with pytest.raises(InvalidApplicationDataError, match="must be an integer"):
        application_factory(data=app_data, user=participant_user, competition=competition, clock=clock, form=form)


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=30)
@given(st.data())
def test_select_field_rejects_unknown_choice(
    participant_user: User,
    organizer_user: User,
    clock: Clock,
    data: st.DataObject,
) -> None:
    """A value not in the SELECT field's choices raises InvalidApplicationDataError."""
    competition = data.draw(valid_competition(organizer_user, clock))
    form = _make_form(
        organizer_user,
        competition,
        clock,
        Field(name="size", label="Size", type=FieldType.SELECT, choices=_CHOICES),
    )
    app_data = data.draw(valid_application_data(domains=competition.domains))
    app_data.form_data = {"size": "XL"}

    with pytest.raises(InvalidApplicationDataError, match="must be one of"):
        application_factory(data=app_data, user=participant_user, competition=competition, clock=clock, form=form)


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=30)
@given(st.data())
def test_multiselect_field_rejects_empty_list(
    participant_user: User,
    organizer_user: User,
    clock: Clock,
    data: st.DataObject,
) -> None:
    """An empty list for a MULTISELECT field raises InvalidApplicationDataError."""
    competition = data.draw(valid_competition(organizer_user, clock))
    form = _make_form(
        organizer_user,
        competition,
        clock,
        Field(name="roles", label="Roles", type=FieldType.MULTISELECT, choices=_MULTI_CHOICES),
    )
    app_data = data.draw(valid_application_data(domains=competition.domains))
    app_data.form_data = {"roles": []}

    with pytest.raises(InvalidApplicationDataError, match="must be a non-empty list"):
        application_factory(data=app_data, user=participant_user, competition=competition, clock=clock, form=form)


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=30)
@given(st.data())
def test_multiselect_field_rejects_invalid_item(
    participant_user: User,
    organizer_user: User,
    clock: Clock,
    data: st.DataObject,
) -> None:
    """A list item not in MULTISELECT choices raises InvalidApplicationDataError."""
    competition = data.draw(valid_competition(organizer_user, clock))
    form = _make_form(
        organizer_user,
        competition,
        clock,
        Field(name="roles", label="Roles", type=FieldType.MULTISELECT, choices=_MULTI_CHOICES),
    )
    app_data = data.draw(valid_application_data(domains=competition.domains))
    app_data.form_data = {"roles": ["fe", "unknown"]}

    with pytest.raises(InvalidApplicationDataError, match="invalid values"):
        application_factory(data=app_data, user=participant_user, competition=competition, clock=clock, form=form)
