# WithdrawApplication

## Input

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| `application_id` | `ApplicationId` | Application to withdraw | UUID format |

## Output

No output. Operation succeeds or raises error.

## Business Rules

1. Application must exist (`APPLICATION_NOT_FOUND`)
2. Only the participant who submitted the application may withdraw it (`ACCESS_DENIED`)
3. Only applications in `PENDING` status can be withdrawn (`APPLICATION_ALREADY_RESOLVED`)
4. Withdrawal is a hard delete — the application record is permanently removed, not transitioned to a new status
