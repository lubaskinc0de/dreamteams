from typing import Any

from dreamteams.entities.application_form.entity import ApplicationForm
from dreamteams.entities.application_form.field import Field, FieldType
from dreamteams.entities.errors.application import InvalidApplicationDataError

MAX_FORM_DATA_DEPTH = 5
MAX_FORM_DATA_FIELDS = 50
MAX_FORM_DATA_FIELD_NAME_LENGTH = 100
MAX_FORM_DATA_INTEGER_ABS = 1_000_000_000
MAX_FORM_DATA_LIST_LENGTH = 50
MAX_FORM_DATA_STRING_LENGTH = 2_000


def _validate_string_field(field: Field, value: Any) -> None:
    if not isinstance(value, str):
        raise InvalidApplicationDataError(message=f"Field '{field.name}' must be a string")
    if len(value) > MAX_FORM_DATA_STRING_LENGTH:
        raise InvalidApplicationDataError(
            message=f"Field '{field.name}' must be at most {MAX_FORM_DATA_STRING_LENGTH} characters",
        )


def _validate_int_field(field: Field, value: Any) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise InvalidApplicationDataError(message=f"Field '{field.name}' must be an integer")
    if abs(value) > MAX_FORM_DATA_INTEGER_ABS:
        raise InvalidApplicationDataError(
            message=f"Field '{field.name}' absolute value must be at most {MAX_FORM_DATA_INTEGER_ABS}",
        )


def _validate_select_field(field: Field, value: Any) -> None:
    if field.choices is None:
        msg = f"SELECT field '{field.name}' has no choices — this is a bug"
        raise RuntimeError(msg)
    valid_values = {c.value for c in field.choices}
    if not isinstance(value, str) or value not in valid_values:
        raise InvalidApplicationDataError(
            message=f"Field '{field.name}' must be one of: {', '.join(sorted(valid_values))}",
        )
    if len(value) > MAX_FORM_DATA_STRING_LENGTH:
        raise InvalidApplicationDataError(
            message=f"Field '{field.name}' must be at most {MAX_FORM_DATA_STRING_LENGTH} characters",
        )


def _validate_multiselect_field(field: Field, value: Any) -> None:
    if field.choices is None:
        msg = f"MULTISELECT field '{field.name}' has no choices — this is a bug"
        raise RuntimeError(msg)
    valid_values = {c.value for c in field.choices}
    if not isinstance(value, list) or not value:
        raise InvalidApplicationDataError(message=f"Field '{field.name}' must be a non-empty list")
    if len(value) > MAX_FORM_DATA_LIST_LENGTH:
        raise InvalidApplicationDataError(
            message=f"Field '{field.name}' must contain at most {MAX_FORM_DATA_LIST_LENGTH} items",
        )
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


def _validate_shape(value: Any, *, path: str, depth: int = 0) -> None:
    if depth > MAX_FORM_DATA_DEPTH:
        raise InvalidApplicationDataError(message=f"Field '{path}' is nested too deeply")

    if isinstance(value, str):
        _validate_shape_string(value, path=path)
        return

    if isinstance(value, bool) or value is None:
        return

    if isinstance(value, int):
        _validate_shape_int(value, path=path)
        return

    if isinstance(value, list):
        _validate_shape_list(value, path=path, depth=depth)
        return

    if isinstance(value, dict):
        _validate_shape_dict(value, path=path, depth=depth)


def _validate_shape_string(value: str, *, path: str) -> None:
    if len(value) > MAX_FORM_DATA_STRING_LENGTH:
        raise InvalidApplicationDataError(
            message=f"Field '{path}' must be at most {MAX_FORM_DATA_STRING_LENGTH} characters",
        )


def _validate_shape_int(value: int, *, path: str) -> None:
    if abs(value) > MAX_FORM_DATA_INTEGER_ABS:
        raise InvalidApplicationDataError(
            message=f"Field '{path}' absolute value must be at most {MAX_FORM_DATA_INTEGER_ABS}",
        )


def _validate_shape_list(value: list[Any], *, path: str, depth: int) -> None:
    if len(value) > MAX_FORM_DATA_LIST_LENGTH:
        raise InvalidApplicationDataError(
            message=f"Field '{path}' must contain at most {MAX_FORM_DATA_LIST_LENGTH} items",
        )
    for index, item in enumerate(value):
        _validate_shape(item, path=f"{path}[{index}]", depth=depth + 1)


def _validate_shape_dict(value: dict[Any, Any], *, path: str, depth: int) -> None:
    if len(value) > MAX_FORM_DATA_FIELDS:
        raise InvalidApplicationDataError(
            message=f"Field '{path}' must contain at most {MAX_FORM_DATA_FIELDS} keys",
        )
    for key, item in value.items():
        _validate_shape_key(key, path=path)
        _validate_shape(item, path=f"{path}.{key}", depth=depth + 1)


def _validate_shape_key(key: Any, *, path: str) -> None:
    if not isinstance(key, str):
        raise InvalidApplicationDataError(message=f"Field '{path}' contains a non-string key")
    if len(key) > MAX_FORM_DATA_FIELD_NAME_LENGTH:
        raise InvalidApplicationDataError(
            message=f"Field '{path}' contains a key longer than {MAX_FORM_DATA_FIELD_NAME_LENGTH} characters",
        )


def _validate_form_data_shape(form_data: dict[str, Any]) -> None:
    if len(form_data) > MAX_FORM_DATA_FIELDS:
        raise InvalidApplicationDataError(
            message=f"form_data must contain at most {MAX_FORM_DATA_FIELDS} fields",
        )
    for key, value in form_data.items():
        if len(key) > MAX_FORM_DATA_FIELD_NAME_LENGTH:
            raise InvalidApplicationDataError(
                message=f"form_data field names must be at most {MAX_FORM_DATA_FIELD_NAME_LENGTH} characters",
            )
        _validate_shape(value, path=key)


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

    _validate_form_data_shape(form_data)

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
