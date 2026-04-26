# ExportApplicationsToSheets

## Purpose

Consumes a pending [ExportApplicationsJob](../entities/export-job.md), builds the spreadsheet for that job's competition and optional status filter, persists the result file, and records the outcome on the job.

## Input

| Field | Type | Description |
|-------|------|-------------|
| `job_id` | `ExportJobId` | The pending job to process |

## Output

No return value — the observable effect is the updated job row (and the persisted spreadsheet).

## Business Rules

1. Rate limit: at most 10 successfully-started jobs per user in any rolling 1-hour window. On breach, the job is marked failed with `EXPORT_RATE_LIMIT_EXCEEDED`. Each job that reaches this interactor counts against the budget whether it ultimately succeeds or fails.
2. The job must exist and be in `pending` status; otherwise `EXPORT_JOB_NOT_FOUND`.
3. The competition application form is read before the spreadsheet session starts. If a form exists, its field names are inserted into the CSV header in form-defined order before the final `Дата` column.
4. Applications are fetched in batches (page size 100) filtered by `job.competition_id` and, when set, `job.application_status`. If `job.application_status is None`, all statuses are exported. The batch loop is visible business logic in the interactor.
5. Rows are streamed into the spreadsheet exporter session as each batch arrives — the interactor never materialises the full application list in memory.
6. Exported columns are `ФИО`, `Соревнование`, `Статус`, `Направления`, `Возраст`, `Тип участника`, `Контакты`, application form fields, and `Дата`. Application IDs, participant IDs, the JSON form-data column, and participant bio are not exported.
7. Submission dates are formatted as `dd.mm.yyyy hh:mm`. Form answer lists are formatted as comma-separated strings.
8. On success: `job.mark_success(file_url, clock)` is committed and the file URL is logged.
9. On any failure (domain error or unexpected exception): `job.mark_failed(reason, clock)` is committed with a short diagnostic `reason`, the in-progress session is aborted, and the exception is re-raised so the worker's retry policy can handle it.

The role check (organizer-only) is enforced upstream by [CreateExportApplicationsJob](create_export_job.md) — a job that reaches this interactor was created by an organizer.

## Errors (recorded on the job, not returned to any caller)

| Error Code | Recorded As | Condition |
|-----------|-------------|-----------|
| `EXPORT_RATE_LIMIT_EXCEEDED` | `status_kind=failed`, `status_reason=<message>` | Caller has started more than 10 jobs in the current hour |
| `EXPORT_JOB_NOT_FOUND` | `status_kind=failed` | The referenced job is missing or already terminal |
| (unexpected exception) | `status_kind=failed`, `status_reason="unexpected: <ExceptionClass>"` | Any non-domain error during fetch / build / upload |
