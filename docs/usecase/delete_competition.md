# DeleteCompetition

## Purpose

Archives competition (soft delete) by organizer who created it.

## Input

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| `competition_id` | `CompetitionId` | Competition identifier | UUID format |

## Output

No output. Operation succeeds or raises error.

## Business Rules

1. Only organizer who created competition can delete it
2. Deletion is soft delete (sets `is_archived = True`)
3. `updated_at` is set to current timestamp
4. Archived competitions are not shown in public listing

## Error Cases

- `AccessDeniedError` — organizer is not competition creator
- `CompetitionNotFoundError` — competition not found
