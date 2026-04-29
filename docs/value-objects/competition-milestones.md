# CompetitionMilestones

## Purpose

Validated collection of competition [Milestone](milestone.md) value objects.

## Business Rules

1. Empty collections are allowed.
2. Milestone timestamps must be unique.

## Possible Errors

- `InvalidCompetitionDataError` — when two milestones share the same timestamp.
