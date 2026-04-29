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
| `description` | `str \| None` | Optional explanatory text (max 300 chars at the application boundary) |

## Validation Rules

1. Title non-empty validation happens at the application boundary.
2. Timestamp is normalized (seconds and microseconds removed).
3. Timestamp should not be in the past when created through the factory.
4. Milestone timestamp uniqueness is owned by [`CompetitionMilestones`](competition-milestones.md).

## Possible Errors

- `InvalidCompetitionDataError` — when a milestone timestamp is in the past or milestone timestamps are not unique

## Used By

- [Competition](../entities/competition.md)
