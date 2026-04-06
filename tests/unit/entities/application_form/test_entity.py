import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from dreamteams.entities.application_form.entity import (
    ApplicationForm,
    ApplicationFormData,
    application_form_factory,
)
from dreamteams.entities.application_form.vo.field import Field, FieldType
from dreamteams.entities.common.clock import Clock
from dreamteams.entities.errors.application_form import InvalidApplicationFormDataError
from dreamteams.entities.errors.base import AccessDeniedError
from dreamteams.entities.user import User
from tests.unit.composite import valid_application_form, valid_application_form_data, valid_competition
from tests.unit.entities.application_form.conftest import STRING_FIELD, make_form, make_form_via_factory

_OTHER_FIELD = Field(name="other", label="Other", type=FieldType.STRING)


def test_empty_fields_list_is_rejected() -> None:
    """ApplicationForm with no fields raises InvalidApplicationFormDataError."""
    with pytest.raises(InvalidApplicationFormDataError, match="at least one field"):
        make_form()


def test_duplicate_field_names_are_rejected() -> None:
    """ApplicationForm with duplicate field names raises InvalidApplicationFormDataError."""
    dup = Field(name="bio", label="Duplicate", type=FieldType.STRING)

    with pytest.raises(InvalidApplicationFormDataError, match="unique names"):
        make_form(STRING_FIELD, dup)


def test_valid_form_is_constructed_correctly() -> None:
    """ApplicationForm stores fields in insertion order."""
    form = make_form(STRING_FIELD, _OTHER_FIELD)

    assert form.fields == [STRING_FIELD, _OTHER_FIELD]


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=30)
@given(st.data())
def test_user_without_organizer_role_is_denied(
    user_without_organizer: User,
    organizer_user: User,
    clock: Clock,
    data: st.DataObject,
) -> None:
    """application_form_factory raises AccessDeniedError for users without an organizer role."""
    competition = data.draw(valid_competition(organizer_user, clock))

    with pytest.raises(AccessDeniedError):
        application_form_factory(
            data=ApplicationFormData(fields=[STRING_FIELD]),
            competition=competition,
            user=user_without_organizer,
            clock=clock,
        )


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=30)
@given(st.data())
def test_organizer_of_different_competition_is_denied(
    different_user: User,
    organizer_user: User,
    clock: Clock,
    data: st.DataObject,
) -> None:
    """application_form_factory raises AccessDeniedError when organizer does not own the competition."""
    competition = data.draw(valid_competition(organizer_user, clock))

    with pytest.raises(AccessDeniedError):
        application_form_factory(
            data=ApplicationFormData(fields=[STRING_FIELD]),
            competition=competition,
            user=different_user,
            clock=clock,
        )


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=30)
@given(st.data())
def test_factory_creates_correct_form(
    organizer_user: User,
    clock: Clock,
    data: st.DataObject,
) -> None:
    """application_form_factory returns an ApplicationForm linked to the competition."""
    competition = data.draw(valid_competition(organizer_user, clock))

    form = make_form_via_factory(organizer_user, competition, clock, STRING_FIELD, _OTHER_FIELD)

    assert form == ApplicationForm(
        id=form.id,
        competition_id=competition.id,
        created_at=form.created_at,
        fields=[STRING_FIELD, _OTHER_FIELD],
    )


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=30)
@given(st.data())
def test_factory_always_succeeds_with_valid_data(
    organizer_user: User,
    clock: Clock,
    data: st.DataObject,
) -> None:
    """application_form_factory succeeds for any valid ApplicationFormData."""
    competition = data.draw(valid_competition(organizer_user, clock))
    form_data = data.draw(valid_application_form_data())

    form = application_form_factory(data=form_data, competition=competition, user=organizer_user, clock=clock)

    assert form.competition_id == competition.id
    assert len(form.fields) == len(form_data.fields)


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=30)
@given(st.data())
def test_factory_result_has_unique_field_names(
    organizer_user: User,
    clock: Clock,
    data: st.DataObject,
) -> None:
    """Field names in the created ApplicationForm are always unique."""
    competition = data.draw(valid_competition(organizer_user, clock))
    form = data.draw(valid_application_form(organizer_user, clock, competition))

    names = [f.name for f in form.fields]

    assert len(names) == len(set(names))
