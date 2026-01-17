# DeleteCompetition

## Input

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| `competition_id` | `CompetitionId` | Competition identifier | UUID format |

## Output

No output. Operation succeeds or raises error.

## Business Rules

1. Only organizer who created competition can delete it
2. Uses hard delete (removes from database via UoW)

## Possible Errors

- `AccessDeniedError` — organizer is not competition creator
- `CompetitionNotFoundError` — competition not found
