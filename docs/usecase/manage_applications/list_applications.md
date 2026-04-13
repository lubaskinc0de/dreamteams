# ListApplicationsByCompetition

## Input

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| `competition_id` | `CompetitionId` | Competition identifier | UUID format |
| `page` | `int` | Page number for pagination | Positive integer |

## Output

| Field | Type | Description |
|-------|------|-------------|
| `items` | `list[ApplicationModel]` | Applications for the current page |
| `total` | `int` | Total number of applications for this competition |
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

1. Competition must exist (`COMPETITION_NOT_FOUND`)
2. Only the organizer who owns the competition may list its applications (`ACCESS_DENIED`)
3. Returns an empty list if no applications have been submitted
4. Results are ordered by `created_at` descending (newest first)
