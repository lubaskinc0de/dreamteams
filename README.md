# DreamTeams

<p align="center">
  <a href="https://dreamteams.luba.skin">
    <img src="https://dreamteams.luba.skin/logo.png" alt="DreamTeams logo" width="120" height="120">
  </a>
</p>

<p align="center">
  <strong>Competition management for hackathons, olympiads, and team-based events.</strong>
</p>

<p align="center">
  <a href="https://dreamteams.luba.skin">Website</a>
  ·
  <a href="docs/index.md">Project documentation</a>
</p>

DreamTeams is a platform where organizers publish competitions and participants discover events, build profiles, submit applications, and track their progress. It is built as a production-style full-stack system: a Nuxt frontend, a FastAPI backend, a separate export worker, strict Clean Architecture boundaries, and rich infrastructure.

## Features

- **Competition discovery.** Visitors and participants can browse public competitions, search by title, filter by tags, registration status, participant type, format, team size, and schedule.
- **Participant profiles.** Participants manage personal information, age, type, experience level, contacts, skills, and avatars.
- **Organizer workflows.** Organizers register through invite codes, create competitions, configure schedules, tracks, participant limits, venues, tags, team formation, and custom application forms.
- **Application lifecycle.** Participants submit applications with form data, organizers review submitted applications, and applications can be accepted, rejected, withdrawn, listed, and exported.
- **Administration.** Admin users manage platform users, block or unblock accounts, issue and revoke organizer invites, and maintain the competition tag catalog.
- **Exports.** Competition applications can be exported to CSV through an asynchronous exporter service backed by Redis, NATS JetStream, and S3-compatible storage.
- **Authentication.** Public traffic is protected by Nginx, OAuth2-Proxy, and Authentik; the application receives a trusted user identifier header after authentication.
- **Observability and quality.** The codebase uses JSON logging, OpenTelemetry, Sentry, strict typing, linting, import boundary checks, and a broad pytest suite.

## Quickstart

### Prerequisites

- Docker and Docker Compose
- Python 3.13
- Node.js for frontend development
- Just
- uv

### Install

```bash
just dev-environment
```

This installs Python development extras through uv and frontend dependencies through npm.

### Run

```bash
just up
```

Detached mode:

```bash
just up-silent
```

Useful local URLs:

- Application through Nginx: `http://localhost`
- API docs through the configured API root: `http://localhost/api/docs`
- OAuth2-Proxy: `http://localhost:4180`
- Authentik setup: `http://127.0.0.1.sslip.io:8080/if/flow/initial-setup/`
- RustFS console: `http://localhost:9001`
- NATS monitor: `http://localhost:8222`

Stop application containers:

```bash
just down
```

Stop the whole compose project:

```bash
just down-all
```

Reset local application data:

```bash
just clear
```

## Development Commands

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
just lint                       # Format, lint, type-check, import-check, typo-check
just build-frontend             # Generate static frontend assets
just docs                       # Serve MkDocs documentation
just generate-migration "Name"  # Generate Alembic migration
```

## Migrations

The main context owns the primary application schema. Migrations live in `src/dreamteams/adapters/db/alembic/` and are applied by the `migrations` container before the API starts.

Generate a migration:

```bash
just generate-migration "Add useful change"
```

The exporter currently stores export jobs in Redis and exported files in S3-compatible storage, so its runtime workflow is intentionally separate from the main relational schema.

## Testing

Run tests:

```bash
just test
```

Run unit tests:

```bash
just test-unit
```

Run quality checks:

```bash
just lint
```

## Architecture

DreamTeams follows Clean Architecture. Business rules live in the inner layers, infrastructure is pushed outward, and dependency direction is enforced by `import-linter`.

```
dreamteams/
├── src/
│   ├── dreamteams/
│   │   ├── entities/          # Domain entities and value objects
│   │   ├── application/       # Use cases, DTOs, ports, Unit of Work protocols
│   │   ├── adapters/          # DB, cache, auth, HTTP, and infrastructure adapters
│   │   ├── presentation/      # FastAPI routers and HTTP error handling
│   │   └── bootstrap/         # Config, DI, logging, CLI, app factories
│   ├── dreamteams_exporter/
│   │   ├── entities/          # Export job domain
│   │   ├── application/       # Export use cases and ports
│   │   ├── adapters/          # Redis, NATS, HTTP, S3, metrics adapters
│   │   ├── presentation/      # Export API and FastStream handlers
│   │   └── bootstrap/         # Exporter API and worker startup
│   └── dreamteams_common/     # Shared errors, interactor, UoW, clock, logging, OTel
├── frontend/                  # Nuxt application
├── docs/                      # Domain and use-case documentation
├── tests/                     # Unit and integration tests
├── docker/                    # Compose and image definitions
├── .config/                   # Local service configuration
├── justfile                   # Development commands
└── pyproject.toml             # Python project metadata and tooling
```

The main and exporter contexts never import each other. They communicate over HTTP and NATS, which keeps each context independently understandable and prevents accidental domain coupling.

### Layers

- **Entities** hold domain models, value objects, identifiers, and domain errors.
- **Application** contains use cases as immutable interactors, gateway protocols, DTOs, and transaction boundaries.
- **Adapters** implement infrastructure details such as SQLAlchemy gateways, Redis caches, HTTP clients, broker publishers, and S3 storage.
- **Presentation** exposes FastAPI routers and FastStream handlers.
- **Bootstrap** wires configuration, logging, dependency injection, migrations, CLIs, and process startup.

### Application Layer

The application layer is organized by use case. Each package under `src/dreamteams/application/` represents a feature:

- `register_user` creates participants, organizers, and superusers;
- `manage_profile` reads, updates, and deletes the current user's profile;
- `publish_competition`, `update_my_competition`, `delete_my_competition`, and `view_my_competitions` cover organizer-owned competition lifecycle;
- `submit_application`, `view_my_applications`, `view_submitted_applications`, and `review_application` cover participant submissions and organizer review;
- `issue_invite`, `view_issued_invites`, `manage_tags`, `view_tags`, `view_users`, `block_user`, and `attach_avatar` cover admin, catalog, profile-media, and account-management workflows.


### Rich Domain Model

DreamTeams uses a rich domain model. Domain objects and value objects protect invariants close to the data they govern:

- `Competition` owns behavior such as updating general info, rescheduling, archive-status changes, schedule validation, team-size rules, participant limits, tracks, tags, milestones, and venue constraints.
- `Application` owns submission and review state transitions: submit, accept, reject, withdraw, already-resolved checks, participant type checks, capacity checks, and ownership checks.
- `OrganizerInvite` owns invite read/use/revoke rules and prevents revoked or already-used invites from being consumed.
- `Participant` and its value objects validate age, skills, contacts, participant type, and profile update rules.
- `ApplicationForm`, `Field`, `ApplicationFormFields`, and related validators ensure form definitions and submitted form data match supported field types and choices.
- The exporter has its own domain model for export jobs and valid job-status transitions.

Factories such as `competition_factory`, `participant_factory`, `application_form_factory`, `application_factory`, and `export_job_factory` create valid entities by applying domain rules at construction time. This keeps invalid state from leaking into later layers.

Domain errors are explicit and typed: access denial, invalid competition data, invalid participant data, invalid form data, invalid application state, invite misuse, capacity overflow, and invalid exporter job transitions are represented as domain/application errors rather than generic exceptions.

The result is that business rules can be tested mostly without FastAPI, SQLAlchemy, Redis, or Docker. Infrastructure tests still matter, but the most important invariants live in pure Python domain code.

## Component Interaction

The local and deployed architecture is intentionally service-oriented:

```
Browser
  -> Nuxt frontend
  -> Nginx
  -> OAuth2-Proxy
  -> Authentik
  -> FastAPI main API
  -> PgBouncer -> PostgreSQL
  -> Redis cache

FastAPI main API
  <- HTTP
  -> Exporter API
  -> Redis export job state
  -> NATS JetStream
  -> Exporter worker
  -> Main API HTTP read endpoints
  -> RustFS / S3-compatible object storage
```

Request flow:

1. The browser loads the Nuxt application and sends API requests through Nginx.
2. Nginx asks OAuth2-Proxy whether the request is authenticated.
3. OAuth2-Proxy validates the session and delegates login to Authentik when needed.
4. Nginx strips untrusted identity headers from public traffic and forwards the configured trusted user header to the backend.
5. The main FastAPI app resolves that external identity through `auth_user` linkage and handles the logic.
6. Database writes go through a Unit of Work and SQLAlchemy gateways; selected hot reads and auth lookups are cached in Redis.
7. Export requests are delegated to the exporter API, which creates Redis-backed job state and publishes a NATS message.
8. The exporter worker consumes the message, fetches applications and form data from the main API over HTTP, streams CSV data to S3-compatible storage, and updates job state.
9. The frontend polls export job status and receives the final private object URL when the export is complete.

## Authentication and Authorization

DreamTeams delegates browser authentication to infrastructure and keeps application code focused on authorization, profile ownership, and domain permissions.

The public request path is:

```text
Browser -> Nginx -> OAuth2-Proxy -> Authentik -> Nginx -> FastAPI
```

- **Authentik** is the identity provider. It owns login, OIDC sessions, user identity, and account verification signals.
- **OAuth2-Proxy** performs the OIDC client flow, stores session state in Redis, and exposes an `auth_request` endpoint for Nginx.
- **Nginx** is the trust boundary. It checks protected routes through OAuth2-Proxy, strips spoofed auth headers from public traffic, and forwards only trusted identity headers to application services.
- **FastAPI** reads the configured user identifier header, resolves it through the `auth_user` table, and then applies application-level authorization rules.

The application stores only the link between external identity and internal user:

- `auth_user.auth_user_id` is the external Authentik subject.
- `auth_user.user_id` points to the internal `users.id`.
- Registration use cases create the internal `User`, attach the requested role profile, and persist the Authentik-to-user link in one transaction.

Authorization is role- and ownership-aware:

- visitors can browse public competition previews;
- participants can maintain participant profiles and manage their own applications;
- organizers can manage only their own competitions, application forms, and submitted applications;
- admins can issue invites, manage tags, inspect users, and block or unblock accounts;
- blocked users are rejected consistently through the authenticated request path, with positive blocked-user cache entries in Redis.

The exporter uses the same trusted identity model. Its HTTP API and worker treat the auth header as an opaque caller identifier and forward it to the main API when reading user, application, and form data. The exporter is therefore intended to run on an internal network behind Nginx, not as a public unauthenticated service.

## Database Structure

The main application uses PostgreSQL with SQLAlchemy in imperative mapping style. Migrations are managed with Alembic and applied on container startup.

<p align="center">
  <img src="https://github.com/user-attachments/assets/046b6be6-55e7-4e8f-b038-986fd05ee6a2" alt="DreamTeams database schema" width="900">
</p>

### Core Tables

- **`users`** stores platform accounts, avatar references, admin status, block status, block reason, block timestamp, and creation timestamp.
- **`auth_user`** links an external Authentik subject to an internal `users.id`.
- **`organizer`** stores organization profiles linked to users, including organizer name, phone number, and contact email.
- **`organizer_invite`** stores invite codes, creator user, display name, revocation state, usage state, the organizer that consumed the invite, and creation time.
- **`participants`** stores participant profiles linked to users, including full name, bio, experience level, participant type, age, and timestamps.
- **`participant_skills`** stores named skill entries with a level per participant.
- **`participant_contacts`** stores custom participant contact methods.

### Competition Tables

- **`competitions`** stores organizer-owned events: title, banner, description, registration window, optional team formation window, participant limits, participant type, format, location, team size, auto-accept flag, archive flag, and timestamps.
- **`competition_tags`** stores reusable searchable tag catalog entries.
- **`competition_tag_links`** connects competitions to tags.
- **`competition_tracks`** stores per-competition tracks or domains.
- **`milestones`** stores dated competition milestones with titles and optional descriptions.

### Application Tables

- **`application_forms`** stores one optional custom form per competition. Field definitions are persisted as structured data and validated by domain value objects.
- **`applications`** stores participant submissions, competition linkage, selected track, status, creation time, and JSON form data. A participant can submit only one application per competition.

### Supporting State

- **Redis** stores read caches, auth lookup caches, blocked-user cache entries, exporter job documents, and export rate-limit counters.
- **RustFS/S3-compatible storage** stores generated CSV export objects and avatars.
- **NATS JetStream** stores export processing messages.

Important database constraints and indexes include unique organizer contacts, unique invite codes, one form per competition, one application per participant and competition, foreign-key cascade behavior, pagination indexes, trigram indexes for search, and tag-link indexes for discovery filters.

## Technology Stack

### Backend

- Python 3.13
- FastAPI
- SQLAlchemy 2.0 async + asyncpg
- Alembic
- Dishka
- Pydantic
- Adaptix
- Redis
- FastStream + NATS JetStream
- aioboto3 with S3-compatible storage
- structlog
- OpenTelemetry
- Sentry

### Frontend

- Nuxt 4
- Vue 3
- TypeScript
- Nuxt UI
- Pinia
- Zod
- Vue Router
- i18n

### Infrastructure

- Docker and Docker Compose
- Nginx
- OAuth2-Proxy
- Authentik
- PostgreSQL
- PgBouncer
- Redis
- NATS
- RustFS
- GitHub Actions

### Quality

- pytest + pytest-xdist
- Hypothesis and Polyfactory for tests
- Ruff
- mypy strict mode
- import-linter
- typos
- uv
- Just

## Observability

- **Structured logs.** `dreamteams_common.logs` configures structlog to emit JSON logs with timestamp, logger name, level, exception details, and OpenTelemetry trace context when a span is active.
- **Trace correlation.** Logs receive `trace_id` and `span_id`, so a backend log line can be tied back to the request or background job span that produced it.
- **OpenTelemetry traces.** `dreamteams_common.observability.setup` configures a global tracer provider and exports spans through OTLP HTTP. Sampling is configurable per service.
- **OpenTelemetry metrics.** A meter provider exports metrics through OTLP on a configurable interval. Domain events feed business counters for registrations, competitions, applications, forms, avatars, and exporter job outcomes.
- **Interactor spans.** The shared `@interactor` decorator wraps use-case execution in spans, making application-layer operations visible without repeating tracing code in every use case.
- **Adapter spans.** Selected database queries, auth verification, and S3 multipart upload steps create explicit spans for slow-path and infrastructure analysis.
- **Sentry.** Sentry configuration exists for backend and exporter processes, allowing unexpected exceptions to be reported separately from handled domain errors.
- **Health probes.** Main and exporter APIs expose liveness and readiness endpoints. Readiness checks include dependencies such as Redis or broker connectivity where appropriate.

## Tests

The test suite is designed around behavior, not implementation details. Unit tests protect domain invariants and pure application rules; integration tests exercise complete use cases through HTTP and real infrastructure adapters.

### Test Layout

- **`tests/unit/`** covers entities, value objects, domain factories, status transitions, access checks, and isolated application behavior.
- **`tests/integration/`** covers public API behavior feature by feature: registration, profiles, competitions, applications, invites, tags, blocking, avatars, and exporter flows.
- **`tests/integration/exporter/`** covers exporter HTTP endpoints and worker processing separately.
- **`tests/common/factory/`** contains Polyfactory factories for API forms, DTOs, and domain test data.
- **`tests/integration/helpers/`** contains feature-level helper gateways that create realistic test state through public APIs or resolved application services.

### Test Infrastructure

Integration tests run the application in process through `httpx.ASGITransport`, so they execute the real FastAPI app, lifespan hooks, Dishka container, routers, error handlers, interactors, gateways, and database adapters without paying the cost of a network server.

External dependencies are real where correctness matters:

- PostgreSQL is provided by testcontainers.
- Alembic migrations are applied once to a template database.
- Each test gets an isolated database cloned from that migrated template with `CREATE DATABASE ... TEMPLATE ...`.
- Redis is provided by testcontainers and flushed between tests.
- RustFS provides S3-compatible storage for avatar and exporter scenarios.
- Exporter tests use in-process FastAPI clients and FastStream/NATS test utilities where possible.

This gives the suite good isolation while keeping integration tests fast enough to run in parallel with pytest-xdist.

### Test Patterns

- **Typed API client.** `tests/integration/api_client.py` wraps HTTP calls and loads responses with Adaptix into application DTOs, so tests assert on real response shapes instead of raw dictionaries.
- **Auth context manager.** `ApiClient.authenticate(...)` uses a `ContextVar`, allowing concurrent async tests or `asyncio.gather` calls to keep separate auth headers.
- **Gateway facade.** Tests inject a `Gateway` facade that groups helper gateways for users, organizers, participants, competitions, applications, forms, invites, tags, and admins.
- **Factories.** Polyfactory generates valid default inputs while tests override only the field relevant to the scenario.
- **Property-based tests.** Hypothesis is used for domain value objects and factory invariants, especially where many input combinations matter.
- **Arrange through public behavior.** Integration helpers prefer creating state through APIs or application services instead of hand-inserting database rows, which keeps tests close to real workflows.
- **Negative-path coverage.** Tests regularly assert unauthorized, forbidden, not found, validation, duplicate, blocked-user, ownership, pagination, and invalid-state behavior.

### Coverage and Quality Bar

The project target is at least **85% coverage** for meaningful backend code. Coverage is useful here as a floor, not the definition of quality: the preferred standard is that every use case has success, permission, validation, ownership, and important failure-path tests.

Good tests in this repository should:

- assert observable behavior rather than private implementation details;
- use factories and helper gateways to keep setup readable;
- isolate test data through per-test databases or explicit cache cleanup;
- include domain edge cases in unit tests and transport/database behavior in integration tests;
- keep one behavioral reason to fail per test where practical;
- cover both main context and exporter context without violating bounded-context imports.

## Code Quality

Code quality is enforced by tooling and architecture contracts:

- **Ruff** handles formatting and linting with a broad `ALL` ruleset.
- **mypy** runs in strict mode with additional error codes enabled.
- **import-linter** enforces Clean Architecture layer direction and bounded-context isolation.
- **typos** catches spelling mistakes in code and documentation.
- **uv** keeps dependency resolution reproducible.

## CI/CD

GitHub Actions workflow: `.github/workflows/lint_test_deploy.yml`.

The pipeline has four main stages:

- **Lint.** Checks out the code, installs Python and uv, installs CI extras, then runs Ruff, mypy, import-linter, and typos.
- **Test.** Runs the pytest suite in a split matrix with `pytest-split` and xdist.
- **Build metadata.** Runs only for version tags and `stage/*` branches. It validates tag placement for releases and prepares deterministic backend and frontend image tags.
- **Build and push.** Builds backend and frontend Docker images with Buildx and pushes them to GitHub Container Registry.

Release behavior:

- version tags such as `v1.2.3` produce versioned backend/frontend images and `latest` tags;
- `stage/*` branches produce stage tags based on the branch name and short commit SHA;
- normal branches and pull requests run lint and tests but do not publish images.

This means every change is checked for style, type safety, architecture boundaries, spelling, and behavior before release artifacts are created.

## Documentation

The detailed domain reference lives in `docs/`:

- [Domain overview](docs/index.md)
- [Entities](docs/entities/index.md)
- [Value objects](docs/value-objects/index.md)
- [Error reference](docs/errors/index.md)
- [Exporter documentation](docs/exporter/index.md)

The exporter context also has a focused service README at [src/dreamteams_exporter/README.md](src/dreamteams_exporter/README.md).
