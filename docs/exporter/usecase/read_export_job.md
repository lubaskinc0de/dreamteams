# ReadExportApplicationsJob

## Purpose

Returns the current state of an export job to its owner so the organizer's client can check progress and retrieve the resulting `file_url` once the job is successful.

## Input

| Field | Type | Description |
|-------|------|-------------|
| `job_id` | `ExportJobId` | The job to fetch |

## Output

The [ExportApplicationsJob](../entities/export-job.md) read model:

| Field | Type | Description |
|-------|------|-------------|
| `id` | `ExportJobId` | Job identifier |
| `user_id` | `UserId` | Owner |
| `competition_id` | `CompetitionId` | Competition being exported |
| `application_status` | `ApplicationStatus \| None` | The filter the job was created with; `None` means unfiltered |
| `status_kind` | `str` | `pending` / `success` / `failed` |
| `status_reason` | `str \| None` | Diagnostic reason when `status_kind == failed` |
| `file_url` | `str \| None` | Populated once `status_kind == success` |
| `created_at` | `datetime` | When the job was accepted |
| `finished_at` | `datetime \| None` | When the terminal transition occurred |

## Business Rules

1. The caller must have a resolvable identity; otherwise `UNAUTHORIZED`.
2. A caller can only read jobs they own. Jobs belonging to another user are hidden — the interactor returns `EXPORT_JOB_NOT_FOUND` rather than leaking existence.
3. A missing job also returns `EXPORT_JOB_NOT_FOUND`; the two cases are intentionally indistinguishable.

## Errors

| Error Code | Condition |
|-----------|-----------|
| `UNAUTHORIZED` | No caller identity is attached to the request |
| `EXPORT_JOB_NOT_FOUND` | Job does not exist **or** the caller does not own it |
