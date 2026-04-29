# AcceptApplication

## Input

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| `application_id` | `ApplicationId` | Application to accept | UUID format |

## Output

No output. Operation succeeds or raises error.

## Business Rules

1. Application must exist (`APPLICATION_NOT_FOUND`)
2. Only the organizer who owns the competition can accept applications (`ACCESS_DENIED`)
3. Only applications in `PENDING` status can be accepted (`APPLICATION_ALREADY_RESOLVED`)
4. Sets application status to `ACCEPTED`
