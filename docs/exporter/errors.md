# Exporter Errors

Errors raised by the exporter's interactors. Returned to the caller on the synchronous paths (create, read) and recorded on the job's `status_reason` on the asynchronous path (process).

| Error Code | Category | Condition |
|------------|----------|-----------|
| `UNAUTHORIZED` | Auth | No caller identity is attached to the request |
| `VALIDATION_ERROR` | Request | Create-job payload is missing or malformed |
| `INVALID_ROLE` | Authorization | Caller is not an organizer (no `organizer_id` on their profile) |
| `EXPORT_RATE_LIMIT_EXCEEDED` | Limits | Caller has already started 10 jobs in the last hour |
| `EXPORT_JOB_NOT_FOUND` | Resource | Job does not exist, is already terminal when processing, or the caller does not own it |
| `INVALID_JOB_STATUS` | Domain invariant | `JobStatus` value object constructed with inconsistent `reason` |
| `INVALID_JOB_STATUS_TRANSITION` | Domain invariant | `mark_success` / `mark_failed` called on a job that is not in `pending` |
| `INTERNAL_SERVER_ERROR` | Fallback | An unexpected exception escaped the interactor |
