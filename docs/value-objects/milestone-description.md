# MilestoneDescription

## Purpose

Free-form context a milestone author can attach to a [`Milestone`](./milestone.md)
(e.g. what the deliverable is, what participants should prepare).

## Type

Value object (frozen dataclass)

## Fields

| Field | Type | Description |
|-------|------|-------------|
| `value` | `str` | The description text |

## Validation Rules

1. `value` must be at most 300 characters

## Possible Errors

- `InvalidCompetitionDataError` — when the value exceeds 300 characters

## Used By

- [Milestone](./milestone.md)
