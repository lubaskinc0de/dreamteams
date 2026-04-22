import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from dreamteams.entities.application_form.vo.field import Field, FieldChoice, FieldType
from dreamteams.entities.errors.application_form import InvalidApplicationFormDataError
from tests.unit.composite import valid_field, valid_text

_CHOICES = (FieldChoice(value="a"), FieldChoice(value="b"))


@pytest.mark.parametrize("blank", ["", "   ", "\t"])
def test_blank_name_is_rejected(blank: str) -> None:
    """Blank field name raises InvalidApplicationFormDataError."""
    with pytest.raises(InvalidApplicationFormDataError, match="Field name must not be empty"):
        Field(name=blank, type=FieldType.STRING)


@pytest.mark.parametrize("ft", [FieldType.SELECT, FieldType.MULTISELECT])
def test_select_type_without_choices_is_rejected(ft: FieldType) -> None:
    """SELECT/MULTISELECT field without choices raises InvalidApplicationFormDataError."""
    with pytest.raises(InvalidApplicationFormDataError, match="must have at least one choice"):
        Field(name="pick", type=ft)


@pytest.mark.parametrize("ft", [FieldType.SELECT, FieldType.MULTISELECT])
def test_select_type_with_empty_choices_is_rejected(ft: FieldType) -> None:
    """SELECT/MULTISELECT field with empty choices tuple raises InvalidApplicationFormDataError."""
    with pytest.raises(InvalidApplicationFormDataError, match="must have at least one choice"):
        Field(name="pick", type=ft, choices=())


@pytest.mark.parametrize("ft", [FieldType.STRING, FieldType.INT])
def test_scalar_type_with_choices_is_rejected(ft: FieldType) -> None:
    """STRING/INT field with choices raises InvalidApplicationFormDataError."""
    with pytest.raises(InvalidApplicationFormDataError, match="must not have choices"):
        Field(name="x", type=ft, choices=_CHOICES)


@pytest.mark.parametrize("ft", [FieldType.SELECT, FieldType.MULTISELECT])
def test_duplicate_choice_values_are_rejected(ft: FieldType) -> None:
    """Duplicate choice values within a field raise InvalidApplicationFormDataError."""
    dup_choices = (FieldChoice(value="x"), FieldChoice(value="x"))

    with pytest.raises(InvalidApplicationFormDataError, match="duplicate choice values"):
        Field(name="pick", type=ft, choices=dup_choices)


@given(name=valid_text())
def test_valid_string_field_is_accepted(name: str) -> None:
    """Any non-blank name produces a valid STRING field."""
    field = Field(name=name, type=FieldType.STRING)

    assert field == Field(name=name, type=FieldType.STRING, required=True, choices=None)


@given(name=valid_text())
def test_valid_int_field_is_accepted(name: str) -> None:
    """Any non-blank name produces a valid INT field."""
    field = Field(name=name, type=FieldType.INT, required=False)

    assert field.required is False
    assert field.choices is None


@given(name=valid_text())
def test_valid_select_field_is_accepted(name: str) -> None:
    """Any non-blank name produces a valid SELECT field."""
    field = Field(name=name, type=FieldType.SELECT, choices=_CHOICES)

    assert field.choices == _CHOICES


@given(name=valid_text())
def test_valid_multiselect_field_is_accepted(name: str) -> None:
    """Any non-blank name produces a valid MULTISELECT field."""
    field = Field(name=name, type=FieldType.MULTISELECT, choices=_CHOICES)

    assert field.choices == _CHOICES


@settings(max_examples=30)
@given(st.data())
def test_any_valid_field_construction_succeeds(data: st.DataObject) -> None:
    """Any field drawn from valid_field() can be constructed without error."""
    field = data.draw(valid_field())

    assert field.name
    if field.type in (FieldType.SELECT, FieldType.MULTISELECT):
        assert field.choices
    else:
        assert field.choices is None
