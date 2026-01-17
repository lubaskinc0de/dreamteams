# Milestone

## Purpose

Represents a competition milestone with timestamp and title.

## Type

Value object (dataclass)

## Fields

| Field | Type | Description |
|-------|------|-------------|
| `timestamp` | `datetime` | Milestone timestamp |
| `title` | `str` | Milestone title |

## Validation Rules

1. Title must not be empty
2. Timestamp is normalized (seconds and microseconds removed)
4. Timestamp should not be in past

## Possible Errors

- `InvalidCompetitionDataError` — when title is empty or timestamps are not unique
