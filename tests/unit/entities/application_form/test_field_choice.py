import pytest
from hypothesis import given

from dreamteams.entities.application_form.vo.field import FieldChoice
from dreamteams.entities.errors.application_form import InvalidApplicationFormDataError
from tests.unit.composite import valid_text


@pytest.mark.parametrize("blank", ["", "   ", "\t"])
def test_blank_value_is_rejected(blank: str) -> None:
    """Blank choice value raises InvalidApplicationFormDataError."""
    with pytest.raises(InvalidApplicationFormDataError, match="Choice value must not be empty"):
        FieldChoice(value=blank, label="Valid")


@pytest.mark.parametrize("blank", ["", "   ", "\t"])
def test_blank_label_is_rejected(blank: str) -> None:
    """Blank choice label raises InvalidApplicationFormDataError."""
    with pytest.raises(InvalidApplicationFormDataError, match="Choice label must not be empty"):
        FieldChoice(value="valid", label=blank)


@given(value=valid_text(), label=valid_text())
def test_non_blank_value_and_label_are_accepted(value: str, label: str) -> None:
    """Any non-blank value and label produce a valid FieldChoice."""
    choice = FieldChoice(value=value, label=label)

    assert choice == FieldChoice(value=value, label=label)
