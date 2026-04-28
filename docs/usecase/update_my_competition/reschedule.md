# RescheduleCompetition

## Input

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| `competition_id` | `CompetitionId` | Competition identifier | UUID format |
| `schedule` | `CompetitionSchedule` | New dates | Value object validation |
| `team_size` | `TeamSizeRange \| None` | New team size | Must be set together with `schedule.team_formation_{start,end}` or both omitted |

## Output

No output. Operation succeeds or raises error.

## Business Rules

1. Only organizer who created competition can reschedule it.
2. `updated_at` is automatically set to current time.
3. General information and archive status are not changed by this interactor.
4. Past schedule dates keep their existing values through `CompetitionSchedule.update`.
5. `team_size` is updated together with schedule because it is paired with team-formation dates.
6. `team_size` and `schedule.team_formation_{start,end}` are a paired group — either all three are provided or all three are omitted. Any mismatch raises `INVALID_COMPETITION_DATA`.
