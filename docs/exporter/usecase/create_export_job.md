# CreateExportApplicationsJob

## Purpose

Accepts an organizer's export request, persists a pending [ExportApplicationsJob](../entities/export-job.md), and emits a processing event so the asynchronous worker picks it up.

## Input

| Field | Type | Description |
|-------|------|-------------|
| `competition_id` | `CompetitionId` | The competition to export |
| `application_status` | `ApplicationStatus` | Filter — only applications in this status are included |

## Output

| Field | Type | Description |
|-------|------|-------------|
| `job_id` | `ExportJobId` | Identifier the caller uses to look up the job later |

## Business Rules

1. The caller must have a resolvable identity; otherwise `UNAUTHORIZED`.
2. The caller must be an organizer (`organizer_id` set on their profile); otherwise the request is rejected with `INVALID_ROLE` and no job row is created.
3. The job is persisted in `pending` status with no `file_url` and no `finished_at`.
4. After persistence, a processing event carrying the new `job_id` is published; the worker-side [ExportApplicationsToSheets](export_applications_to_sheets.md) consumes it.
5. Rate limits are enforced downstream at processing time, not here.

## Errors

| Error Code | Condition |
|-----------|-----------|
| `UNAUTHORIZED` | No caller identity is attached to the request |
| `INVALID_ROLE` | Caller is not an organizer |
| `VALIDATION_ERROR` | `competition_id` or `application_status` missing / malformed |
