# FieldChoice

## Purpose

Represents a single selectable option within a `SELECT` or `MULTISELECT` field of an ApplicationForm.

## Type

Value object (immutable dataclass)

## Attributes

| Attribute | Type  | Description                                              |
| --------- | ----- | -------------------------------------------------------- |
| `value`   | `str` | Machine-readable key stored in the application form data |

## Business Rules

1. Non-empty `value` validation happens at the application boundary.
2. All `FieldChoice.value` items within a single `Field` must be unique.
