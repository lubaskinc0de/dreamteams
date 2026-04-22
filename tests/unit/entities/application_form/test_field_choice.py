import pytest
from hypothesis import given

from dreamteams.entities.application_form.vo.field import FieldChoice
from dreamteams.entities.errors.application_form import InvalidApplicationFormDataError
from tests.unit.composite import valid_text


@pytest.mark.parametrize("blank", ["", "   ", "\t"])
def test_blank_value_is_rejected(blank: str) -> None:
    """Blank choice value raises InvalidApplicationFormDataError."""
    with pytest.raises(InvalidApplicationFormDataError, match="Choice value must not be empty"):
        FieldChoice(value=blank)


@given(value=valid_text())
def test_non_blank_value_is_accepted(value: str) -> None:
    """Any non-blank value produces a valid FieldChoice."""
    choice = FieldChoice(value=value)

    assert choice == FieldChoice(value=value)
