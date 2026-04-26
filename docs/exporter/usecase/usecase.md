# Export Applications to Sheets

## Purpose

Lets an organizer download every application submitted to one of their competitions, filtered by status, as a spreadsheet. The flow is split across three interactors:

| Interactor | When it runs |
|------------|--------------|
| [CreateExportApplicationsJob](create_export_job.md) | Synchronously, when the organizer requests an export |
| [ExportApplicationsToSheets](export_applications_to_sheets.md) | Asynchronously, after the job is created |
| [ReadExportApplicationsJob](read_export_job.md) | Synchronously, whenever the organizer checks on a job |

## End-to-end flow

```
Organizer
    │
    │  "export these applications"
    ▼
CreateExportApplicationsJob
    ├── role check
    ├── persist pending job
    └── emit processing event
              │
              ▼
    ExportApplicationsToSheets   (runs asynchronously, potentially on another process)
    ├── rate-limit check
    ├── fetch application form structure
    ├── fetch applications in batches
    ├── stream rows into the spreadsheet
    └── mark_success(file_url) OR mark_failed(reason)
              │
              ▼
Organizer
    │  "how is job X doing?"
    ▼
ReadExportApplicationsJob
    └── returns ExportJobModel with status + file_url
```

## Business Rules (cross-interactor)

1. Only organizers may initiate exports. Participants and anonymous callers are rejected at creation with `INVALID_ROLE`; no job row is persisted.
2. Each job is private to its creator — another user, even another organizer, cannot read or observe it.
3. Rate limiting is per user, enforced at processing time: each accepted job that enters the worker counts against the 10-per-rolling-hour budget. Over-budget jobs are marked `failed` with `EXPORT_RATE_LIMIT_EXCEEDED`.
4. Failures are recorded on the job (`status_kind = failed`, `status_reason = <message>`); the caller retries by creating a new job.
5. The spreadsheet uses fixed application/participant columns plus application-form columns in form-defined order. Form field names become CSV column names.
