# ListMyApplications

## Input

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| `page` | `int` | Page number for pagination | Positive integer |

## Output

| Field | Type | Description |
|-------|------|-------------|
| `items` | `list[ApplicationModel]` | Applications for the current page |
| `total` | `int` | Total number of applications submitted by this participant |
| `page` | `int` | Current page number |

### ApplicationModel

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

1. User must have a Participant profile (`ACCESS_DENIED`)
2. Returns only applications submitted by the current participant
3. Returns an empty list if the participant has submitted no applications
4. Results are ordered by `created_at` descending (newest first)
