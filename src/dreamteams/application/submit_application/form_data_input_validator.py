from typing import Any

_PathPart = str | int

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
        _validate_shape(value, path=[key])


def _validate_shape(value: Any, *, path: list[_PathPart], depth: int = 0) -> None:
    if depth > MAX_FORM_DATA_DEPTH:
        msg = f"Field '{_format_path(path)}' is nested too deeply"
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


def _validate_shape_string(value: str, *, path: list[_PathPart]) -> None:
    if len(value) > MAX_FORM_DATA_STRING_LENGTH:
        msg = f"Field '{_format_path(path)}' must be at most {MAX_FORM_DATA_STRING_LENGTH} characters"
        raise ValueError(msg)


def _validate_shape_int(value: int, *, path: list[_PathPart]) -> None:
    if abs(value) > MAX_FORM_DATA_INTEGER_ABS:
        msg = f"Field '{_format_path(path)}' absolute value must be at most {MAX_FORM_DATA_INTEGER_ABS}"
        raise ValueError(msg)


def _validate_shape_list(value: list[Any], *, path: list[_PathPart], depth: int) -> None:
    if len(value) > MAX_FORM_DATA_LIST_LENGTH:
        msg = f"Field '{_format_path(path)}' must contain at most {MAX_FORM_DATA_LIST_LENGTH} items"
        raise ValueError(msg)
    for index, item in enumerate(value):
        path.append(index)
        _validate_shape(item, path=path, depth=depth + 1)
        path.pop()


def _validate_shape_dict(value: dict[Any, Any], *, path: list[_PathPart], depth: int) -> None:
    if len(value) > MAX_FORM_DATA_FIELDS:
        msg = f"Field '{_format_path(path)}' must contain at most {MAX_FORM_DATA_FIELDS} keys"
        raise ValueError(msg)
    for key, item in value.items():
        _validate_shape_key(key, path=path)
        path.append(key)
        _validate_shape(item, path=path, depth=depth + 1)
        path.pop()


def _validate_shape_key(key: Any, *, path: list[_PathPart]) -> None:
    if not isinstance(key, str):
        msg = f"Field '{_format_path(path)}' contains a non-string key"
        raise TypeError(msg)
    if len(key) > MAX_FORM_DATA_FIELD_NAME_LENGTH:
        msg = f"Field '{_format_path(path)}' contains a key longer than {MAX_FORM_DATA_FIELD_NAME_LENGTH} characters"
        raise ValueError(msg)


def _format_path(path: list[_PathPart]) -> str:
    result = str(path[0])
    for part in path[1:]:
        if isinstance(part, int):
            result += f"[{part}]"
        else:
            result += f".{part}"
    return result
