# ParticipantLimits

## Purpose

Defines the maximum number of participants allowed in a competition.

## Type

Value object (dataclass)

## Fields

| Field | Type | Description |
|-------|------|-------------|
| `max` | `int` | Maximum participants |

## Validation Rules

1. `max` must be greater than 0

## Possible Errors

- `InvalidCompetitionDataError` — when validation rules are violated
