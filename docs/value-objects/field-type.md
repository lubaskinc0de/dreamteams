# FieldType

## Purpose

Represents the data type of a single field in an ApplicationForm.

## Type

Value object (Enum)

## Values

| Value         | Description                                                                 |
| ------------- | --------------------------------------------------------------------------- |
| `STRING`      | Free-text string input                                                      |
| `INT`         | Integer numeric input                                                       |
| `SELECT`      | Single choice from a predefined list of options (`choices` must be set)     |
| `MULTISELECT` | Multiple choices from a predefined list of options (`choices` must be set)  |

## Business Rules

1. For `SELECT` and `MULTISELECT` types the field must have a non-empty `choices` list.
2. For `STRING` and `INT` types the `choices` list must be absent (or empty).
