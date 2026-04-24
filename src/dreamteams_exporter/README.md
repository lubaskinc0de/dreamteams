# dreamteams_exporter

Bounded context responsible for exporting a competition's applications to a CSV file stored in S3. Lives alongside the main `dreamteams` package under `src/`; the two communicate over HTTP + NATS and never import each other's Python code.

## What it does

1. An authenticated caller asks for an export — `POST /exports/`.
2. The exporter persists a pending job in Redis and publishes a NATS message on `exporter.jobs.process`.
3. A FastStream worker picks the message up, streams applications from the main context, serialises them into CSV, and streams the bytes straight to S3 via multipart upload.
4. The caller polls `GET /exports/{job_id}` for the finished URL.

## Identity + trust model

- A single string identifier (the value of `<auth-header>`) travels across every hop. The exporter neither parses nor validates it beyond presence — it's opaque from the exporter's perspective.
- `IdProvider` is request-scoped, one implementation per entry point (`HttpIdProvider` reads from `Request`, `MessageIdProvider` reads from `NatsMessage`). Both extract the header in `__init__` and hydrate the caller's `User` lazily via `/users/me`.
- Trust relies on four invariants: (a) NATS broker bound to compose network only, (b) exporter's FastAPI port bound to compose network only, (c) main's app container port bound to compose network only, (d) Nginx strips the auth header from public traffic. Breaking any of them enables user impersonation.

## Deploy unit

Two processes, same container image:

- `dreamteams-exporter run api` — FastAPI on `ServerConfig.port` (default 8001).
- `dreamteams-exporter run worker` — FastStream NATS subscriber.

Both read `EXPORTER_CONFIG_PATH` (TOML).
