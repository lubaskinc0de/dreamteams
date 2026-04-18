set windows-powershell := true

up:
    just down
    just build-frontend
    docker compose -f docker/docker-compose.yml --env-file=./.config/.env up --build

up-server:
    just down
    docker compose -f docker/docker-compose.yml --env-file=./.config/.env up --build

up-silent:
    docker compose -f docker/docker-compose.yml --env-file=./.config/.env up --build -d

up-db:
    docker compose -f docker/docker-compose.yml --env-file=./.config/.env up db -d

test:
    just down
    docker compose -f docker/docker-compose.tests.yml --env-file=./.config/.env up --build --abort-on-container-exit tests
    just down

test-unit:
    pytest -vvv tests/unit

down:
    docker compose -f docker/docker-compose.yml --env-file=./.config/.env down
    docker compose -f docker/docker-compose.tests.yml --env-file=./.config/.env down

clear:
    docker compose -f docker/docker-compose.yml --env-file=./.config/.env down -v

lint:
    ruff format
    ruff check --fix
    mypy
    lint-imports
    typos

dev-environment:
    pip install uv
    uv pip install -e ".[dev]"
    cd ./frontend; npm install

generate-migration NAME:
    just up-db
    sleep 1s
    set -a && source ./.config/.env.migrations.local && set +a && dreamteams migrations autogenerate "{{NAME}}"
    just down

cookie-secret:
    echo "OAUTH2_PROXY_COOKIE_SECRET=$(openssl rand -base64 32)"

build-frontend:
    cd ./frontend; npm run generate

docs:
    mkdocs serve


# --- Profiling ---------------------------------------------------------------
profile-up:
    PROFILE_BUILD=1 docker compose -f docker/docker-compose.yml --env-file=./.config/.env up --build api -d

# Record a flamegraph from the running api process.
profile DURATION="30":
    mkdir -p ./profiling
    docker exec -u root api py-spy record --pid 1 --duration {{DURATION}} --rate 100 --idle --output /tmp/flame.svg
    docker cp api:/tmp/flame.svg ./profiling/flame-$(date -u +%Y%m%dT%H%M%SZ).svg
    ls -lh ./profiling/ | tail -1

# Live top
profile-top:
    docker exec -u root -it api py-spy top --pid 1 --rate 100

# Per-thread stack dump at the moment of execution. Useful when something hangs.
profile-dump:
    docker exec -u root api py-spy dump --pid 1