# ListApplicationsByCompetition

## Input

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| `competition_id` | `CompetitionId` | Competition identifier | UUID format |
| `page` | `int` | Page number for pagination | Positive integer (default `1`) |
| `sort_by` | `str` | Field to sort by | `created_at` (default) |
| `sort_order` | `str` | Sort order | `asc` or `desc` (default `desc`) |
| `status` | `str \| null` | Filter by application status | `pending` / `accepted` / `rejected` (default: no filter) |

## Output

| Field | Type | Description |
|-------|------|-------------|
| `items` | `list[ApplicationModel]` | Applications for the current page |
| `total` | `int` | Total number of applications matching the filter |
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
3. Returns an empty list if no applications match the filter
4. Results are ordered by `sort_by` in `sort_order`, with `id` as a stable tiebreaker
5. `status`, when provided, narrows results to that status only
