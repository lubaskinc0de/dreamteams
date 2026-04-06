from typing import Any

from dreamteams.entities.application_form.entity import ApplicationForm
from dreamteams.entities.application_form.vo.field import Field, FieldType
from dreamteams.entities.errors.application import InvalidApplicationDataError


def _validate_string_field(field: Field, value: Any) -> None:
    if not isinstance(value, str):
        raise InvalidApplicationDataError(message=f"Field '{field.name}' must be a string")


def _validate_int_field(field: Field, value: Any) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise InvalidApplicationDataError(message=f"Field '{field.name}' must be an integer")


def _validate_select_field(field: Field, value: Any) -> None:
    if field.choices is None:
        msg = f"SELECT field '{field.name}' has no choices — this is a bug"
        raise RuntimeError(msg)
    valid_values = {c.value for c in field.choices}
    if not isinstance(value, str) or value not in valid_values:
        raise InvalidApplicationDataError(
            message=f"Field '{field.name}' must be one of: {', '.join(sorted(valid_values))}",
        )


def _validate_multiselect_field(field: Field, value: Any) -> None:
    if field.choices is None:
        msg = f"MULTISELECT field '{field.name}' has no choices — this is a bug"
        raise RuntimeError(msg)
    valid_values = {c.value for c in field.choices}
    if not isinstance(value, list) or not value:
        raise InvalidApplicationDataError(message=f"Field '{field.name}' must be a non-empty list")
    invalid = [v for v in value if not isinstance(v, str) or v not in valid_values]
    if invalid:
        raise InvalidApplicationDataError(
            message=f"Field '{field.name}' contains invalid values: {', '.join(str(v) for v in invalid)}",
        )


_FIELD_VALIDATORS = {
    FieldType.STRING: _validate_string_field,
    FieldType.INT: _validate_int_field,
    FieldType.SELECT: _validate_select_field,
    FieldType.MULTISELECT: _validate_multiselect_field,
}


def validate_form_data(
    form_data: dict[str, Any] | None,
    form: ApplicationForm | None,
) -> None:
    """Validate form_data answers against an ApplicationForm schema."""
    if form is None:
        if form_data is not None:
            raise InvalidApplicationDataError(
                message="form_data must be None when the competition has no application form",
            )
        return

    field_map = {f.name: f for f in form.fields}

    if form_data is None:
        missing = [f.name for f in form.fields if f.required]
        if missing:
            raise InvalidApplicationDataError(
                message=f"Missing required form fields: {', '.join(missing)}",
            )
        return

    extra = set(form_data) - field_map.keys()
    if extra:
        raise InvalidApplicationDataError(
            message=f"Unknown form fields: {', '.join(sorted(extra))}",
        )

    for field in form.fields:
        if field.name not in form_data:
            if field.required:
                raise InvalidApplicationDataError(message=f"Required field '{field.name}' is missing")
            continue
        _FIELD_VALIDATORS[field.type](field, form_data[field.name])
