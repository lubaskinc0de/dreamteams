# FieldChoice

## Purpose

Represents a single selectable option within a `SELECT` or `MULTISELECT` field of an ApplicationForm.

## Type

Value object (immutable dataclass)

## Attributes

| Attribute | Type  | Description                                              |
| --------- | ----- | -------------------------------------------------------- |
| `value`   | `str` | Machine-readable key stored in the application form data |
| `label`   | `str` | Human-readable display text shown to participants        |

## Business Rules

1. `value` must not be empty or whitespace-only.
2. `label` must not be empty or whitespace-only.
3. All `FieldChoice.value` items within a single `Field` must be unique.
