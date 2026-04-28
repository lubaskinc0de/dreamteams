from hypothesis import given

from dreamteams.entities.application_form.field import FieldChoice
from tests.unit.composite import valid_text


@given(value=valid_text())
def test_non_blank_value_is_accepted(value: str) -> None:
    """Any non-blank value produces a valid FieldChoice."""
    choice = FieldChoice(value=value)

    assert choice == FieldChoice(value=value)
