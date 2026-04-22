# CompetitionSchedule

## Purpose

Defines competition timeline with registration and optional team formation periods.

## Type

Value object (dataclass)

## Fields

| Field | Type | Description |
|-------|------|-------------|
| `registration_start` | `datetime` | Registration period start |
| `registration_end` | `datetime` | Registration period end |
| `team_formation_start` | `datetime \| None` | Team formation period start (optional) |
| `team_formation_end` | `datetime \| None` | Team formation period end (optional) |

## Validation Rules

1. All dates are normalized (seconds and microseconds removed)
2. All dates must not be in the past
3. `registration_start` must be before `registration_end`
4. If team formation is specified, both start and end must be provided together
5. `team_formation_start` must be after or equal to `registration_end`
6. `team_formation_end` must be after `team_formation_start`

## Cross-Value-Object Invariant

`team_formation_start`/`team_formation_end` are paired with the owning `Competition`'s [`team_size`](team-size-range.md): either all three are set or all three are `None`. This invariant is enforced at the `Competition` entity level (factory and `update`), not inside this value object, because it crosses two value objects.

## Possible Errors

- `InvalidCompetitionDataError` — when validation rules are violated

## Used By

- [Competition](../entities/competition.md)
