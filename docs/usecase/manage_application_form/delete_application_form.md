# DeleteApplicationForm

## Input

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| `competition_id` | `CompetitionId` | Competition identifier | UUID format |

## Output

No output. Operation succeeds or raises error.

## Business Rules

1. Competition must exist (`COMPETITION_NOT_FOUND`)
2. Only the organizer who owns the competition can delete its form (`ACCESS_DENIED`)
3. Form must exist for the competition (`APPLICATION_FORM_NOT_FOUND`)
