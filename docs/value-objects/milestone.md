# Milestone

## Purpose

Represents a competition milestone with timestamp, title, and optional description.

## Type

Value object (dataclass)

## Fields

| Field | Type | Description |
|-------|------|-------------|
| `timestamp` | `datetime` | Milestone timestamp |
| `title` | `str` | Milestone title |
| `description` | [`MilestoneDescription`](./milestone-description.md) \| `None` | Optional explanatory text (max 300 chars) |

## Validation Rules

1. Title must not be empty
2. Timestamp is normalized (seconds and microseconds removed)
3. Timestamp should not be in past
4. Description, when provided, must satisfy [`MilestoneDescription`](./milestone-description.md) validation

## Possible Errors

- `InvalidCompetitionDataError` — when title is empty, timestamps are not unique, or description exceeds its max length

## Used By

- [Competition](../entities/competition.md)
