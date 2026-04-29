# DreamTeams Exporter

A bounded context responsible for exporting competition applications to a CSV file in S3. Lives in `src/dreamteams_exporter/` as a sibling package of `dreamteams`; the two communicate only over HTTP and NATS.

---

## Actors

| Actor | Description |
|-------|-------------|
| **Organizer** | The only role permitted to request exports. Each organizer's exports are private to that organizer. |

Participants and unauthenticated callers are rejected with `INVALID_ROLE`.

---

## Entities

- [ExportApplicationsJob](entities/export-job.md) — the aggregate root tracking one export from request through terminal success/failure.

## Value Objects

- [JobStatus](value-objects/job-status.md) — the pending/success/failed state of a job, with reason required on failure.

## Use Cases

- [Export Applications to Sheets](usecase/usecase.md) — create a pending job, process it asynchronously, and read its status back.
  - [CreateExportApplicationsJob](usecase/create_export_job.md) — organizer requests an export (HTTP, synchronous).
  - [ExportApplicationsToSheets](usecase/export_applications_to_sheets.md) — worker builds the CSV and uploads to S3 (NATS, asynchronous).
  - [ReadExportApplicationsJob](usecase/read_export_job.md) — owner polls the job's status (HTTP, synchronous).

## Frontend API

- [Public HTTP API](public-http-api.md) — frontend-facing routes, payloads, polling flow, and error codes.

## Errors

- [Error Reference](errors.md) — exporter-specific error codes.
