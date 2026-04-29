# JobStatus

## Purpose

Discriminated value object describing the current state of an [ExportApplicationsJob](../entities/export-job.md). A failed job carries a human-readable reason; a pending or successful job never does.

## Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `kind` | [`JobStatusKind`](#jobstatuskind-enum) | Discriminator: pending / success / failed |
| `reason` | `str \| None` | Set **iff** `kind == FAILED`; `None` for every other kind |

## JobStatusKind (Enum)

| Value | Description |
|-------|-------------|
| `PENDING` | Job accepted, not yet processed |
| `SUCCESS` | Job finished; the owning job's `file_url` is populated |
| `FAILED` | Job terminated with an error; `reason` holds the short diagnostic string |

## Business Rules

1. `kind == FAILED` requires a non-`None` `reason`; constructing without one raises `INVALID_JOB_STATUS`.
2. `kind != FAILED` forbids a non-`None` `reason`; setting one raises `INVALID_JOB_STATUS`.
3. Prefer the classmethod constructors over direct construction: `JobStatus.pending()`, `JobStatus.success()`, `JobStatus.failed("reason")`.
4. The VO is frozen — transitions happen by assigning a new `JobStatus` to the owning job, never by mutating an existing one.
