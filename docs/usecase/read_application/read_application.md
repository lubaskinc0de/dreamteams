# ReadApplication

## Input

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| `application_id` | `ApplicationId` | Application identifier | UUID format |

## Output

| Field | Type | Description |
|-------|------|-------------|
| `id` | `ApplicationId` | Application identifier |
| `participant_id` | `ParticipantId` | Participant who submitted the application |
| `competition_id` | `CompetitionId` | Target competition |
| `domains` | `list[Domain]` | Domains the participant selected |
| `status` | `ApplicationStatus` | Current status: `PENDING`, `ACCEPTED`, or `REJECTED` |
| `created_at` | `datetime` | Submission timestamp |
| `form_data` | `dict[str, Any] \| None` | Form answers, or `None` if no form was required |

## Business Rules

1. Application must exist (`APPLICATION_NOT_FOUND`)
2. Only the participant who submitted the application or the organizer who owns the competition may read it (`ACCESS_DENIED`)
