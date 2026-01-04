# TeamSizeRange

## Purpose

Defines minimum and maximum team size for competition.

## Type

Value object (dataclass)

## Fields

| Field | Type | Description |
|-------|------|-------------|
| `max` | `int` | Maximum team size |
| `min` | `int` | Minimum team size |

## Validation Rules

1. `min` must be at least 1
2. `max` must be greater than 0
3. `min` must be less than or equal to `max`

## Possible Errors

- `InvalidCompetitionDataError` — when validation rules are violated
