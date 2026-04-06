# Field

## Purpose

Describes a single input field inside an ApplicationForm that a participant must fill in when applying to a competition.

## Type

Value object (immutable dataclass)

## Attributes

| Attribute   | Type                              | Description                                                                    |
| ----------- | --------------------------------- | ------------------------------------------------------------------------------ |
| `name`      | `str`                             | Machine-readable unique identifier for the field within the form               |
| `label`     | `str`                             | Human-readable label displayed to the participant                              |
| `type`      | `FieldType`                       | Data type of the field (STRING, INT, SELECT, MULTISELECT)                      |
| `required`  | `bool`                            | Whether the participant must supply a value for this field (default: `True`)   |
| `choices`   | `tuple[FieldChoice, ...] \| None` | Available options; required for SELECT / MULTISELECT, absent otherwise         |

## Business Rules

1. `name` must not be empty or whitespace-only.
2. `label` must not be empty or whitespace-only.
3. For `SELECT` and `MULTISELECT` types, `choices` must be provided and contain at least one item.
4. For `STRING` and `INT` types, `choices` must be `None`.
5. All `FieldChoice.value` items within a field must be unique.

## Relationships

```
Field ──> FieldType
Field 1 ──> N FieldChoice   (only for SELECT / MULTISELECT)
```
