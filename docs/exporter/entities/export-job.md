# ExportApplicationsJob

## Purpose

Represents a single organizer-initiated export of a competition's applications to a CSV file. Owned by the exporter bounded context; the main context sees a job only through the exporter's HTTP surface.

## Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `id` | `ExportJobId` (UUID) | Unique job identifier |
| `user_id` | `UserId` (UUID) | The organizer who requested the export (soft reference) |
| `competition_id` | `CompetitionId` (UUID) | The competition whose applications are being exported (soft reference) |
| `application_status` | `ApplicationStatus \| None` | Optional filter; `None` exports all applications |
| `status` | [`JobStatus`](../value-objects/job-status.md) | Current state of the job (pending / success / failed) |
| `file_url` | `str \| None` | URL of the uploaded CSV once `status.kind == success`; otherwise `None` |
| `created_at` | `datetime` | Timestamp the job was accepted |
| `finished_at` | `datetime \| None` | Timestamp of the terminal transition; `None` while the job is pending |

All references to main-context identifiers (`user_id`, `competition_id`) are **soft** — the exporter stores raw UUIDs with no foreign key into the main schema.

## Business Rules

1. A job is created in `pending` status via the factory; no other initial state is valid.
2. Only the organizer who created a job can read it back.
3. Only organizers (i.e. users with `organizer_id is not None`) may create and process jobs; participants and anonymous callers are rejected with `INVALID_ROLE`.
4. Export is rate-limited per user: at most 10 jobs can be processed in any rolling 1-hour window.
5. Terminal transitions — `mark_success(file_url, clock)` and `mark_failed(reason, clock)` — are allowed only from `pending`. Re-entering either state raises `INVALID_JOB_STATUS_TRANSITION`.
6. `finished_at` is set exactly once, at the terminal transition.
7. Retries are explicit: a failed job is not re-processed in place; the caller creates a new job.

## Lifecycle

```
             ┌──────────────┐
             │   pending    │◀─ factory
             └──────┬───────┘
                    │
       ┌────────────┴────────────┐
       │                         │
       ▼                         ▼
┌──────────────┐          ┌──────────────┐
│   success    │          │    failed    │
│ (file_url,   │          │   (reason,   │
│ finished_at) │          │ finished_at) │
└──────────────┘          └──────────────┘
```

## Relationships

```
ExportApplicationsJob N ──> 1 Organizer   (soft ref via user_id)
ExportApplicationsJob N ──> 1 Competition (soft ref via competition_id)
```

No cascades — if the competition or organizer is deleted in the main context, the exporter's historical jobs are preserved (the `file_url` may 404 when followed).
