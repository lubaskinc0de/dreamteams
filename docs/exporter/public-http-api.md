# Exporter Public HTTP API

Frontend code should call the exporter through Nginx under the same public `/api` surface as the main backend. Do not call the internal exporter container or port directly.

## Base Path

```text
/api/exports
```

Nginx protects these routes with OAuth2-Proxy and forwards the authenticated user headers to the exporter. Browser requests should use the normal session cookies/credentials flow already used for the main API.

## Types

```ts
export type ApplicationStatus = "pending" | "accepted" | "rejected";
export type ExportJobStatusKind = "pending" | "success" | "failed";

export interface CreateExportJobInput {
  competition_id: string;
  application_status?: ApplicationStatus | null;
}

export interface CreatedExportJob {
  job_id: string;
}

export interface ExportJobModel {
  id: string;
  user_id: string;
  competition_id: string;
  application_status: ApplicationStatus | null;
  status_kind: ExportJobStatusKind;
  status_reason: string | null;
  file_url: string | null;
  created_at: string;
  finished_at: string | null;
}
```

## Create Export Job

```http
POST /api/exports/
Content-Type: application/json
```

Body:

```json
{
  "competition_id": "9c6caa6e-8314-4a18-8bb3-28cc8a7e0d2a",
  "application_status": "accepted"
}
```

Omit `application_status` or send `null` to export all applications without status filtering:

```json
{
  "competition_id": "9c6caa6e-8314-4a18-8bb3-28cc8a7e0d2a"
}
```

Response `200`:

```json
{
  "job_id": "8ae64f99-b6e5-4d46-8f29-af55d2fc22db"
}
```

This only creates and schedules the export. The CSV is produced asynchronously.

## Read Export Job

```http
GET /api/exports/{job_id}
```

Response `200` while processing:

```json
{
  "id": "8ae64f99-b6e5-4d46-8f29-af55d2fc22db",
  "user_id": "8d45a02d-b7e4-46d8-ae1d-7c53b9bd0cbb",
  "competition_id": "9c6caa6e-8314-4a18-8bb3-28cc8a7e0d2a",
  "application_status": null,
  "status_kind": "pending",
  "status_reason": null,
  "file_url": null,
  "created_at": "2026-04-25T12:00:00Z",
  "finished_at": null
}
```

Response `200` after success:

```json
{
  "id": "8ae64f99-b6e5-4d46-8f29-af55d2fc22db",
  "user_id": "8d45a02d-b7e4-46d8-ae1d-7c53b9bd0cbb",
  "competition_id": "9c6caa6e-8314-4a18-8bb3-28cc8a7e0d2a",
  "application_status": "accepted",
  "status_kind": "success",
  "status_reason": null,
  "file_url": "http://localhost/s3/exports/exports%2F8ae64f99-b6e5-4d46-8f29-af55d2fc22db.csv",
  "created_at": "2026-04-25T12:00:00Z",
  "finished_at": "2026-04-25T12:00:05Z"
}
```

When `status_kind` is `success`, render `file_url` as the download/open link. When `status_kind` is `failed`, show `status_reason` if present.

CSV columns are exported in this order:

```text
ФИО, Соревнование, Статус, Направления, Возраст, Тип участника, Контакты, <application form fields>, Дата
```

## Frontend Flow

1. Organizer clicks export for a competition.
2. Frontend sends `POST /api/exports/`.
3. Frontend stores `job_id`.
4. Frontend polls `GET /api/exports/{job_id}` until `status_kind` is `success` or `failed`.
5. On `success`, use `file_url`; on `failed`, stop polling and show an error state.

A 1-2 second polling interval is enough.

## Errors

Errors use the same envelope as the main API:

```ts
interface ApiError {
  code: string;
  message: string;
  meta: Record<string, unknown> | null;
}
```

Common exporter errors:

| Status | Code | Meaning |
|--------|------|---------|
| `401` | `UNAUTHORIZED` | Missing/invalid authenticated session. |
| `403` | `INVALID_ROLE` | Caller is not an organizer. |
| `404` | `EXPORT_JOB_NOT_FOUND` | Job does not exist or belongs to another user. |
| `422` | `VALIDATION_ERROR` | Invalid payload or UUID. |
| `429` | `EXPORT_RATE_LIMIT_EXCEEDED` | Too many export attempts in the rate-limit window. |
