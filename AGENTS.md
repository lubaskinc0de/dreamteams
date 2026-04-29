# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

DreamTeams is a competition management platform built with a strict Clean Architecture approach, inheriting from the "crudik" template. The backend is Python-based using FastAPI, SQLAlchemy, and Dishka for dependency injection. The application manages users, organizers, and competitions with multi-layer authentication via Authentik and OAuth2-Proxy.

## Development Commands

### Essential Commands (Just)

```bash
just up              # Start all services in development mode
just up-silent       # Start all services in detached mode
just down            # Stop all services
just clear           # Stop all services and remove volumes (cleans database)
just test            # Run integration tests in Docker
just test-unit       # Run unit tests locally
just lint            # Run ruff, mypy, import-linter, and typos
just dev-environment # Install development dependencies locally with uv
```

### Database Migrations

```bash
just generate-migration "Description"  # Generate new migration (starts db, creates migration, stops db)
```

Migrations are automatically applied on startup in docker-compose.

### Frontend

```bash
just build-frontend  # Build Nuxt.js frontend (generates static assets)
just reload          # Full reload: down, build frontend, up
```

## Architecture

### Clean Architecture Layers

The project enforces strict layer boundaries via `import-linter` (configured in `.importlinter`):

1. **entities/** - Core domain models (User, Organizer, Competition)
   - Must NOT import from: application, adapters, presentation, bootstrap
   - Contains: domain entities, value objects, domain errors
   - Type aliases for identifiers: `UserId`, `OrganizerId`, `CompetitionId` (all UUID-based)

2. **application/** - Use cases and business logic
   - Must NOT import from: adapters, presentation, bootstrap
   - Contains: interactors (use cases), gateway interfaces (ports), UoW protocol
   - Interactors are immutable dataclasses decorated with `@interactor`
   - Defines protocols that adapters must implement (Dependency Inversion)

3. **adapters/** - Infrastructure implementations
   - Must NOT import from: presentation, bootstrap
   - Contains: database gateways, auth providers, SQLAlchemy models
   - Implements interfaces defined in application layer

4. **presentation/** - HTTP interface (sub-layer of adapters)
   - Must NOT import from: bootstrap
   - Contains: FastAPI routers, request/response models, error handlers

5. **bootstrap/** - Application initialization
   - Contains: DI container setup, config loading, logging setup, CLI entry point
   - No import restrictions

### Key Patterns

**Interactors**: Use cases are implemented as frozen dataclasses with dependencies injected via constructor. Use the `@interactor` decorator from `application/common/interactor.py`.

**Unit of Work (UoW)**: Transaction management protocol defined in `application/common/uow.py`. All database modifications must go through UoW (`.add()`, `.commit()`, `.delete()`, `.flush()`).

**Gateways**: Database access interfaces defined in `application/common/gateway/` and implemented in `adapters/db/gateway/`. Never use SQLAlchemy models directly in application layer.

**Dependency Injection**: Uses Dishka. Container configured in `bootstrap/di/container.py` with providers in `bootstrap/di/providers/`.

## Configuration

**Config Loading**: `Config.load()` in `bootstrap/config/loader.py` loads from:
- TOML file at path specified by `CONFIG_PATH` env var (default: `.config/config.toml`)
- Environment variables for database connection, server host/port

**Config Structure**:
- `auth` - Authentication headers configuration
- `tracing` - Request tracing configuration
- `cors` - CORS policy
- `api` - API root path
- Database config loaded separately from env vars

## Authentication Flow

Multi-layer architecture: **Client → Nginx → OAuth2-Proxy → Authentik → Application**

1. Nginx intercepts all requests with `auth_request /oauth2/auth`
2. OAuth2-Proxy validates session cookie (stored in Redis)
3. If unauthenticated, redirects to Authentik OIDC login
4. After successful auth, OAuth2-Proxy sets user ID header
5. Nginx forwards configured header to application
6. Application resolves `AuthUser` → `User` via database lookup

**User Linking**: When creating users, `UserFactory` (in `application/register/shared/user_factory.py`) creates both `User` entity and `AuthUser` record linking the Authentik subject to the application user ID.

**Header Configuration**: User ID header name is configurable in `.config/config.toml` under `[auth].user_id_header`.

## Testing

**Integration Tests**: Run in Docker Compose via `just test` using `docker/docker-compose.tests.yml`. Tests use:
- Fake JWT tokens signed with dummy private key (see `tests/integration/conftest.py`)
- Database cleanup between tests
- `ApiClient` helper class for making authenticated requests

**Test Structure**:
- `tests/integration/` - Integration tests by feature (register, manage_profile, manage_competitions)
- `tests/unit/` - Unit tests
- `tests/common/factory/` - Polyfactory factories for test data

**Running Tests**:
- `just test` - Full integration test suite in Docker
- `just test-unit` - Unit tests locally (requires local environment)

## Database

**ORM**: SQLAlchemy 2.0 in imperative style (no declarative base inheritance)

**Models**: Located in `src/dreamteams/adapters/db/models/`

**Migrations**: Alembic migrations in `src/dreamteams/adapters/db/alembic/`. Auto-applied on container startup.

**Connection**: AsyncPG driver, connection config from environment variables (see `DbConfig.from_env()` in `adapters/db/config.py`)

## CI/CD

GitHub Actions workflow in `.github/workflows/lint_test_deploy.yml`:

1. **lint** - Runs ruff, mypy, import-linter (always)
2. **test** - Integration tests in Docker (always)
3. **bump_version** - Semantic versioning (master branch only)
4. **build_and_push** - Docker images to GHCR (master and dev branches)

**Versioning**:
- master: `v0.0.1`, `latest`
- dev: `v0.0.1-dev`, `latest-dev`

## Code Quality

**Strict Type Checking**: mypy with `strict = true` enabled. All code must pass type checking.

**Linting**: Ruff with extensive ruleset (`select = ['ALL']`). Auto-formatting with `ruff format`.

**Layer Enforcement**: import-linter validates architecture boundaries. Violations will fail CI.

**Typos**: Typos checker configured in `_typos.toml`.

## Entry Points

**CLI**: `dreamteams` command (defined in `pyproject.toml` scripts)
- Implemented in `bootstrap/cli.py`
- Used for running migrations: `dreamteams migrations autogenerate "message"`

**API**: FastAPI app factory in `bootstrap/fast_api.py`

## Common Development Scenarios

**Adding a New Entity**:
1. Create entity class in `entities/`
2. Add type alias to `entities/common/identifiers.py` if needed
3. Create SQLAlchemy model in `adapters/db/models/`
4. Create gateway interface in `application/common/gateway/`
5. Implement gateway in `adapters/db/gateway/`
6. Generate migration: `just generate-migration "Add entity table"`

**Adding a New Use Case**:
1. Create interactor in `application/{feature}/` as frozen dataclass with `@interactor` decorator
2. Define dependencies (UoW, gateways) as class attributes
3. Implement `async def execute()` method
4. Register in DI container (`bootstrap/di/providers/interactor.py`)
5. Create FastAPI router in `presentation/fast_api/routers/`
6. Add integration tests in `tests/integration/{feature}/`

**Logging**: Use structlog. Get logger with `structlog.get_logger(__name__)`. All logs output as JSON with automatic trace ID injection when configured.

## Bounded Contexts

`src/` holds three sibling Python packages — not one monolith:

- **`dreamteams`** — the main app (users, organizers, competitions, applications, invites).
- **`dreamteams_exporter`** — the export-to-spreadsheet service. Owns its own schema (`exporter`), its own alembic chain, FastAPI on a separate internal port, and a FastStream NATS worker. See `src/dreamteams_exporter/README.md`.
- **`dreamteams_common`** — shared primitives only: `AppError`, `@interactor`, `UoW` protocol, `Clock`/`SystemClock`, `Logger` alias, structlog bootstrap, `OTelConfig` + `setup_observability`. Nothing domain-specific.

**Import-linter enforces the boundaries.** All 11 contracts in `.importlinter`:

- Each context's 4 layer-boundary contracts (entities ↛ application/adapters/presentation/bootstrap, etc.).
- `dreamteams_exporter` ↛ `dreamteams` and `dreamteams` ↛ `dreamteams_exporter` — the two contexts never import each other's Python. They communicate over the wire (HTTP + NATS).
- `dreamteams_common` ↛ `dreamteams` | `dreamteams_exporter` — the shared lib can't reach downward into either context.

If you see an import-linter failure, the fix is almost always at the protocol/DTO layer — duplicate the tiny transport shape into each context (the cost of a few extra dataclasses is much lower than the cost of giving up the boundary).

**Running both contexts locally**: `just up` starts main + exporter + Postgres + Redis + NATS + S3 in one compose network. Both app containers bind internal-only ports; Nginx proxies only main's public surface.

**Adding a third bounded context**: scaffold as `src/dreamteams_<name>/` with the same 5-layer tree, register it in `pyproject.toml` (`[tool.uv.build-backend] module-name`), add the 4 layer contracts plus 2 cross-context forbidden contracts to `.importlinter`, and have it talk to the others via HTTP or NATS — never via Python imports. Shared primitives that genuinely belong to every context go in `dreamteams_common`; anything else stays local.
