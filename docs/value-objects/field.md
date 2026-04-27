# Field

## Purpose

Describes a single input field inside an ApplicationForm that a participant must fill in when applying to a competition.

## Type

Value object (immutable dataclass)

## Attributes

| Attribute   | Type                              | Description                                                                    |
| ----------- | --------------------------------- | ------------------------------------------------------------------------------ |
| `name`      | `str`                             | Machine-readable unique identifier for the field within the form               |
| `type`      | [`FieldType`](field-type.md)                       | Data type of the field (STRING, INT, SELECT, MULTISELECT)                      |
| `required`  | `bool`                            | Whether the participant must supply a value for this field (default: `True`)   |
| `choices`   | `tuple[`[`FieldChoice`](field-choice.md)`, ...] \| None` | Available options; required for SELECT / MULTISELECT, absent otherwise         |

## Business Rules

1. Non-empty `name` validation happens at the application boundary.
2. For `SELECT` and `MULTISELECT` types, `choices` must be provided and contain at least one item.
3. For `STRING` and `INT` types, `choices` must be `None`.
4. All `FieldChoice.value` items within a field must be unique.

## Relationships

```
Field ──> FieldType
Field 1 ──> N FieldChoice   (only for SELECT / MULTISELECT)
```
