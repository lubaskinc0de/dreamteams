from typing import Any

MAX_FORM_DATA_DEPTH = 5
MAX_FORM_DATA_FIELDS = 50
MAX_FORM_DATA_FIELD_NAME_LENGTH = 100
MAX_FORM_DATA_INTEGER_ABS = 1_000_000_000
MAX_FORM_DATA_LIST_LENGTH = 50
MAX_FORM_DATA_STRING_LENGTH = 2_000


def validate_form_data_input_bounds(form_data: dict[str, Any]) -> None:
    """Validate application-level request bounds for dynamic form answers."""
    if len(form_data) > MAX_FORM_DATA_FIELDS:
        msg = f"form_data must contain at most {MAX_FORM_DATA_FIELDS} fields"
        raise ValueError(msg)
    for key, value in form_data.items():
        if len(key) > MAX_FORM_DATA_FIELD_NAME_LENGTH:
            msg = f"form_data field names must be at most {MAX_FORM_DATA_FIELD_NAME_LENGTH} characters"
            raise ValueError(msg)
        _validate_shape(value, path=key)


def _validate_shape(value: Any, *, path: str, depth: int = 0) -> None:
    if depth > MAX_FORM_DATA_DEPTH:
        msg = f"Field '{path}' is nested too deeply"
        raise ValueError(msg)

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
        msg = f"Field '{path}' must be at most {MAX_FORM_DATA_STRING_LENGTH} characters"
        raise ValueError(msg)


def _validate_shape_int(value: int, *, path: str) -> None:
    if abs(value) > MAX_FORM_DATA_INTEGER_ABS:
        msg = f"Field '{path}' absolute value must be at most {MAX_FORM_DATA_INTEGER_ABS}"
        raise ValueError(msg)


def _validate_shape_list(value: list[Any], *, path: str, depth: int) -> None:
    if len(value) > MAX_FORM_DATA_LIST_LENGTH:
        msg = f"Field '{path}' must contain at most {MAX_FORM_DATA_LIST_LENGTH} items"
        raise ValueError(msg)
    for index, item in enumerate(value):
        _validate_shape(item, path=f"{path}[{index}]", depth=depth + 1)


def _validate_shape_dict(value: dict[Any, Any], *, path: str, depth: int) -> None:
    if len(value) > MAX_FORM_DATA_FIELDS:
        msg = f"Field '{path}' must contain at most {MAX_FORM_DATA_FIELDS} keys"
        raise ValueError(msg)
    for key, item in value.items():
        _validate_shape_key(key, path=path)
        _validate_shape(item, path=f"{path}.{key}", depth=depth + 1)


def _validate_shape_key(key: Any, *, path: str) -> None:
    if not isinstance(key, str):
        msg = f"Field '{path}' contains a non-string key"
        raise TypeError(msg)
    if len(key) > MAX_FORM_DATA_FIELD_NAME_LENGTH:
        msg = f"Field '{path}' contains a key longer than {MAX_FORM_DATA_FIELD_NAME_LENGTH} characters"
        raise ValueError(msg)
