import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from dreamteams.entities.application_form.entity import (
    ApplicationForm,
    ApplicationFormData,
    application_form_factory,
)
from dreamteams.entities.application_form.vo.field import Field, FieldType
from dreamteams.entities.application_form.vo.fields import ApplicationFormFields
from dreamteams.entities.errors.base import AccessDeniedError
from dreamteams_common.clock import Clock
from tests.unit.composite import valid_application_form, valid_application_form_data, valid_competition
from tests.unit.entities.application_form.conftest import STRING_FIELD, make_form, make_form_via_factory
from tests.unit.helpers.facade import Gateway

_OTHER_FIELD = Field(name="other", type=FieldType.STRING)


def test_valid_form_is_constructed_correctly() -> None:
    """ApplicationForm stores fields in insertion order."""
    form = make_form(STRING_FIELD, _OTHER_FIELD)

    assert form.fields == [STRING_FIELD, _OTHER_FIELD]


@settings(max_examples=30)
@given(st.data())
def test_organizer_of_different_competition_is_denied(
    gateway: Gateway,
    clock: Clock,
    data: st.DataObject,
) -> None:
    """application_form_factory raises AccessDeniedError when organizer does not own the competition."""
    organizer = gateway.organizer.create()
    different_organizer = gateway.organizer.create()
    competition = data.draw(valid_competition(organizer, clock))

    with pytest.raises(AccessDeniedError):
        application_form_factory(
            data=ApplicationFormData(fields=ApplicationFormFields([STRING_FIELD])),
            competition=competition,
            organizer=different_organizer,
            clock=clock,
        )


@settings(max_examples=30)
@given(st.data())
def test_factory_creates_correct_form(
    gateway: Gateway,
    clock: Clock,
    data: st.DataObject,
) -> None:
    """application_form_factory returns an ApplicationForm linked to the competition."""
    organizer = gateway.organizer.create()
    competition = data.draw(valid_competition(organizer, clock))

    form = make_form_via_factory(organizer, competition, clock, STRING_FIELD, _OTHER_FIELD)

    assert form == ApplicationForm(
        id=form.id,
        competition_id=competition.id,
        created_at=form.created_at,
        fields=ApplicationFormFields([STRING_FIELD, _OTHER_FIELD]),
    )


@settings(max_examples=30)
@given(st.data())
def test_factory_always_succeeds_with_valid_data(
    gateway: Gateway,
    clock: Clock,
    data: st.DataObject,
) -> None:
    """application_form_factory succeeds for any valid ApplicationFormData."""
    organizer = gateway.organizer.create()
    competition = data.draw(valid_competition(organizer, clock))
    form_data = data.draw(valid_application_form_data())

    form = application_form_factory(
        data=form_data,
        competition=competition,
        organizer=organizer,
        clock=clock,
    )

    assert form.competition_id == competition.id
    assert len(form.fields) == len(form_data.fields)


@settings(max_examples=30)
@given(st.data())
def test_factory_result_has_unique_field_names(
    gateway: Gateway,
    clock: Clock,
    data: st.DataObject,
) -> None:
    """Field names in the created ApplicationForm are always unique."""
    organizer = gateway.organizer.create()
    competition = data.draw(valid_competition(organizer, clock))
    form = data.draw(valid_application_form(organizer, clock, competition))

    names = [f.name for f in form.fields]

    assert len(names) == len(set(names))
