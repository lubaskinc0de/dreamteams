# UpdateCompetition

## Purpose

Updates existing competition by organizer who created it.

## Input

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| `competition_id` | `CompetitionId` | Competition identifier | UUID format |
| `title` | `str \| None` | New competition title | Max 200 characters |
| `description` | `str \| None` | New competition description | Non-empty |
| `schedule` | `CompetitionSchedule \| None` | New competition and registration dates | Value object validation |
| `participant_limits` | `ParticipantLimits \| None` | New min/max participant count | Value object validation |
| `domains` | `list[Domain] \| None` | New competition technical domains | Non-empty list |
| `participant_type` | `ParticipantType \| None` | New participation type | Enum value |
| `venue` | `CompetitionVenue \| None` | New competition format and location | Value object validation |
| `team_size` | `TeamSizeRange \| None` | New min/max team size | Value object validation |
| `is_archived` | `bool \| None` | Archive status | Boolean value |

## Output

No output. Operation succeeds or raises error.

## Business Rules

1. Only organizer who created competition can update it
2. `updated_at` is set to current timestamp
3. All validation rules from `CompetitionSchedule`, `CompetitionVenue`, `ParticipantLimits`, `TeamSizeRange` apply
4. Fields with `None` value are not updated

## Error Cases

- `AccessDeniedError` — organizer is not competition creator
- `CompetitionNotFoundError` — competition not found
- `InvalidCompetitionDataError` — validation failed for updated fields
