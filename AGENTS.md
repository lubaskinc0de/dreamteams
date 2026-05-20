# AGENTS.md

Guidance for AI agents working in this repository.

## Project Overview

DreamTeams is a competition management platform for hackathons, olympiads, and team-based events. It has a Nuxt frontend, a FastAPI main API, and a separate exporter service for asynchronous CSV exports.

The backend follows strict Clean Architecture and is split into bounded contexts under `src/`:

- `dreamteams` - main context: users, organizers, participants, competitions, applications, invites, tags, and profiles.
- `dreamteams_exporter` - export context: export jobs, NATS processing, HTTP reads from the main API, and S3-compatible CSV storage.
- `dreamteams_common` - shared primitives only: `AppError`, `@interactor`, `UoW`, clock, logger aliases, structlog setup, and OpenTelemetry setup.

The main and exporter contexts must not import each other. They communicate over HTTP and NATS.

## Essential Commands

Use `just` recipes unless a task needs a narrower command.

```bash
just up                         # Start the local stack in the foreground
just up-silent                  # Start the local stack detached
just up-db                      # Start PostgreSQL only
just down                       # Stop app-facing containers
just down-all                   # Stop all compose services
just clear                      # Reset app DB and selected volumes
just clear-all                  # Remove all compose volumes
just test                       # Run pytest with xdist
just test-cov                   # Run pytest with coverage
just test-unit                  # Run unit tests
just lint                       # Run ruff format/check --fix, mypy, import-linter, typos
just dev-environment            # Install Python dev extras and frontend dependencies
just build-frontend             # Generate static frontend assets
just docs                       # Serve MkDocs documentation
just generate-migration "Name"  # Generate Alembic migration
```

`just test` runs pytest locally with xdist. It does not start a Docker test compose file.

## Architecture Rules

Import boundaries are enforced by `.importlinter`.

Main context:

- `dreamteams.entities` must not import application, adapters, presentation, or bootstrap.
- `dreamteams.application` must not import adapters, presentation, or bootstrap.
- `dreamteams.adapters` must not import presentation or bootstrap.
- `dreamteams.presentation` must not import bootstrap.

Exporter context follows the same layer rules.

Cross-context rules:

- `dreamteams` must not import `dreamteams_exporter`.
- `dreamteams_exporter` must not import `dreamteams`.
- `dreamteams_common` must not import either bounded context.

If an import-linter failure appears, fix it at the protocol, DTO, or transport boundary. Prefer duplicating a tiny transport shape in each context over coupling contexts through Python imports.

## Backend Patterns

- Use immutable dataclass interactors decorated with `@interactor`.
- Keep use cases in `application/{feature}/`.
- Define ports in the application layer and implement them in adapters.
- Do not use SQLAlchemy models directly from application code.
- Route database writes through the Unit of Work protocol.
- Register interactors and adapters in Dishka providers under `bootstrap/di/providers/`.
- Keep domain-specific code out of `dreamteams_common`.
- Use structured DTOs and value objects instead of ad hoc dictionaries when the codebase already has a type for the shape.

Application-layer organization:

- Group code by business capability or use-case family, not by technical pattern.
- Keep orchestration in interactors: load through gateways, delegate decisions to domain objects, persist through UoW, publish events, return DTOs.
- Keep infrastructure out of interactors; add or extend gateway protocols when a use case needs persistence, cache, storage, broker, auth, or HTTP access.
- Put request/response DTOs near the use case when they are feature-specific; put shared DTOs under `application/common/dto`.

Domain-model expectations:

- Prefer rich entities and value objects over passive records plus scattered procedural checks.
- Put invariants where the data lives: competition schedule/team-size rules in competition objects, application status transitions in application objects, invite lifecycle rules in invite objects, profile validation in participant/organizer value objects.
- Use domain factories to construct valid entities and prevent invalid state from entering later layers.
- Raise explicit domain/application errors rather than generic exceptions for business-rule failures.
- Unit-test domain behavior directly before adding broader integration coverage.

## Database and Persistence

The main application uses PostgreSQL with SQLAlchemy 2.0 imperative mappings.

Important model groups:

- `users` and `auth_user` for internal users and Authentik subject linkage.
- `organizer` and `organizer_invite` for organizer registration and invite lifecycle.
- `participants`, `participant_skills`, and `participant_contacts` for participant profiles.
- `competitions`, `competition_tags`, `competition_tag_links`, `competition_tracks`, and `milestones` for competition publishing and discovery.
- `application_forms` for custom per-competition forms.
- `applications` for participant submissions and review status.

Migrations live in `src/dreamteams/adapters/db/alembic/`. Generate them with:

```bash
just generate-migration "Description"
```

The exporter stores export job state in Redis, queues processing through NATS JetStream, and stores generated CSV files in S3-compatible storage. Do not model exporter jobs in the main app schema unless the product requirement explicitly changes.

## Component Interaction

Request flow:

1. Browser loads the Nuxt frontend and sends requests through Nginx.
2. Nginx uses OAuth2-Proxy's auth endpoint for protected routes.
3. OAuth2-Proxy validates session state in Redis and redirects to Authentik when login is needed.
4. Nginx forwards a trusted user identifier header to the application.
5. The main FastAPI API resolves the external subject through `auth_user`.
6. Use cases run through interactors, gateways, Unit of Work, PostgreSQL, and Redis caches.
7. Export requests go to the exporter API, which creates Redis job state and publishes a NATS message.
8. The exporter worker consumes the message, reads application data from the main API over HTTP, streams CSV to S3-compatible storage, and updates Redis job state.

Trust assumptions:

- Public traffic must go through Nginx.
- Nginx must strip spoofed auth headers.
- Exporter API, exporter worker, NATS, Redis, and internal API ports are intended to run on the compose or deployment network, not as public user-facing services.

## Authentication

The stack is:

```text
Client -> Nginx -> OAuth2-Proxy -> Authentik -> FastAPI
```

The application does not run the browser login flow itself. It expects the configured auth header after OAuth2-Proxy has validated the session. User registration links the external Authentik subject to an internal `User` through `auth_user`.

Header configuration is in `.config/config.toml` under `[auth]`.

## Frontend

The frontend lives in `frontend/` and uses:

- Nuxt 4
- Vue 3
- TypeScript
- Nuxt UI
- Pinia
- Zod
- i18n

The root `frontend/README.md` may lag behind the actual product. Inspect `frontend/app/pages`, `frontend/app/components`, `frontend/app/stores`, and `frontend/app/composables` before relying on it.

Build static assets with:

```bash
just build-frontend
```

## Testing

Test layout:

- `tests/integration/` - use-case and API integration tests.
- `tests/unit/` - domain and application unit tests.
- `tests/common/factory/` - Polyfactory factories.
- `tests/integration/exporter/` - exporter workflow tests.

Test patterns to preserve:

- Integration tests run FastAPI in process through `httpx.ASGITransport`.
- PostgreSQL and Redis are provided by testcontainers.
- Alembic migrations are applied once to a template database, then each test clones an isolated DB from it.
- Redis is flushed between tests.
- The typed `ApiClient` loads responses into DTOs and exposes auth through a `ContextVar`-based context manager.
- Helper gateway facades create realistic state for tests.
- Polyfactory provides valid defaults; tests override only scenario-specific fields.
- Hypothesis is used for domain/value-object invariants where input space matters.

Use focused tests when changing a narrow feature, then broaden to `just test` when the change affects shared behavior, persistence, auth, or cross-context interactions. The project coverage target is at least 85% for meaningful backend code; use coverage as a floor, not as a replacement for success, permission, validation, ownership, and failure-path assertions.

## Code Quality

The project is intentionally strict:

- mypy strict mode is enabled.
- Ruff uses a broad `ALL` ruleset.
- import-linter enforces layer and bounded-context contracts.
- typos checks spelling.
- CI runs linting and split pytest jobs.

`just lint` rewrites files through `ruff format` and `ruff check --fix`. Avoid running it when the task is read-only or when unrelated user changes are present and you only need a non-mutating check.

Quality expectations:

- Keep application code dependent on protocols, not concrete adapters.
- Keep SQLAlchemy and transport details out of entities and interactors.
- Preserve bounded-context isolation even when duplicating a small DTO feels repetitive.
- Prefer behavior-level tests over private implementation assertions.
- Add tests for negative paths, not only happy paths.

## Observability

The runtime uses structlog, OpenTelemetry, and Sentry.

- Logs are JSON and include trace/span context when active.
- `@interactor` wraps use-case execution in OpenTelemetry spans.
- Selected adapters add spans around database queries, auth verification, and S3 multipart upload steps.
- Domain event handlers emit business metrics for registrations, competitions, applications, forms, avatars, and exporter jobs.
- Sentry is configured per process for unexpected exceptions.

When adding behavior, prefer logs with stable structured fields (`user_id`, `competition_id`, `application_id`, `job_id`) and avoid logging secrets, raw tokens, invite codes, passwords, or uploaded file contents.

## CI/CD

GitHub Actions workflow: `.github/workflows/lint_test_deploy.yml`.

Jobs:

- `lint` - Ruff, mypy, import-linter, typos.
- `test` - split pytest matrix.
- `build_metadata` - prepares image tags for version tags and `stage/*` branches.
- `build_backend` - builds and pushes backend image to GHCR.
- `build_frontend` - builds and pushes frontend image to GHCR.

## Common Development Scenarios

Adding a use case:

1. Add or update entities/value objects only if the domain needs it.
2. Add application-layer input/output DTOs and an interactor.
3. Add or extend gateway protocols in the application layer.
4. Implement persistence or external access in adapters.
5. Register dependencies in Dishka.
6. Expose the behavior through FastAPI or FastStream presentation.
7. Add focused tests under the matching test feature directory.

Adding a table:

1. Add the domain model or value object.
2. Add the SQLAlchemy imperative model in adapters.
3. Add gateway protocol and implementation.
4. Generate an Alembic migration.
5. Add integration coverage for persistence-facing behavior.

Adding cross-context behavior:

1. Define the wire contract explicitly.
2. Keep request/response DTOs local to each context.
3. Communicate by HTTP, NATS, or another external protocol.
4. Do not import Python from the other bounded context.

## Documentation Sources

- Root README: high-level project overview.
- `docs/index.md`: domain and use-case documentation.
- `docs/errors/index.md`: API error reference.
- `docs/exporter/index.md`: exporter behavior.
- `src/dreamteams_exporter/README.md`: exporter service notes.
- `GETTING_STARTED.md`: onboarding notes.

Prefer updating the closest documentation source when behavior changes.
