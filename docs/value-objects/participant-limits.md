# ParticipantLimits

## Purpose

Defines minimum and maximum number of participants allowed in competition.

## Type

Value object (dataclass)

## Fields

| Field | Type | Description |
|-------|------|-------------|
| `max` | `int` | Maximum participants |
| `min` | `int` | Minimum participants |

## Validation Rules

1. `max` must be greater than 0
2. `min` must be greater than 0
3. `min` must be less than or equal to `max`

## Possible Errors

- `InvalidCompetitionDataError` — when validation rules are violated
