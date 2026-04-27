import pytest

from dreamteams.entities.application_form.vo.field import Field, FieldType
from dreamteams.entities.application_form.vo.fields import ApplicationFormFields
from dreamteams.entities.errors.application_form import InvalidApplicationFormDataError


def test_empty_fields_list_is_rejected() -> None:
    """ApplicationFormFields rejects an empty list."""
    with pytest.raises(InvalidApplicationFormDataError, match="Application form must have at least one field"):
        ApplicationFormFields([])


def test_duplicate_field_names_are_rejected() -> None:
    """ApplicationFormFields rejects duplicate field names."""
    with pytest.raises(
        InvalidApplicationFormDataError,
        match="Application form fields must have unique names",
    ):
        ApplicationFormFields(
            [
                Field(name="bio", type=FieldType.STRING),
                Field(name="bio", type=FieldType.INT),
            ],
        )


def test_unique_field_names_are_accepted() -> None:
    """ApplicationFormFields accepts fields with unique names."""
    fields = ApplicationFormFields(
        [
            Field(name="bio", type=FieldType.STRING),
            Field(name="age", type=FieldType.INT),
        ],
    )

    assert len(fields) == 2
