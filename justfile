set windows-powershell := true

up:
    just down
    docker compose -f docker/docker-compose.yml up --build

up-server:
    just down
    docker compose -f docker/docker-compose.yml up --build

up-silent:
    docker compose -f docker/docker-compose.yml up --build -d

up-db:
    docker compose -f docker/docker-compose.yml up db -d

test:
    pytest -vvv -n auto --dist=worksteal

test-cov:
    pytest -vvv -n auto --cov=src --cov-report=term-missing

test-unit:
    pytest -vvv tests/unit -n auto --dist=worksteal --cov=src/dreamteams/entities --cov-report=term-missing

down:
    docker compose -f docker/docker-compose.yml stop frontend migrations api exporter-api exporter-worker
    docker compose -f docker/docker-compose.yml rm -f frontend migrations api exporter-api exporter-worker

down-all:
    docker compose -f docker/docker-compose.yml down

clear:
    docker compose -f docker/docker-compose.yml down
    docker compose -f docker/docker-compose.yml up db -d --wait
    docker compose -f docker/docker-compose.yml exec -T db psql -U postgres -d postgres < ./.config/reset-app-db.sql
    docker compose -f docker/docker-compose.yml down
    docker volume rm -f docker_redis_data docker_nats_data docker_rustfs_data

clear-all:
    docker compose -f docker/docker-compose.yml down -v

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
    APP_CONFIG_PATH=./.config/migrations.local.toml dreamteams migrations autogenerate "{{NAME}}"
    just down

cookie-secret:
    echo "OAUTH2_PROXY_COOKIE_SECRET=$(openssl rand -base64 32)"

authentik-console:
    @echo "Authentik setup:  http://127.0.0.1.sslip.io:8080/if/flow/initial-setup/"
    @echo "Authentik admin:  http://127.0.0.1.sslip.io:8080/if/admin/"
    @echo "Default user:     akadmin (password chosen during initial setup)"

build-frontend:
    cd ./frontend; npm run generate

docs:
    mkdocs serve


# --- Profiling ---------------------------------------------------------------
profile-up:
    PROFILE_BUILD=1 docker compose -f docker/docker-compose.yml up --build api -d

# Print the hottest uvicorn worker PID inside the api container.
profile-pid:
    @docker exec -u root api /venv/bin/python3 -c 'import os,sys; vals=[]; [vals.append((int(open("/proc/"+p+"/stat").read().split()[13])+int(open("/proc/"+p+"/stat").read().split()[14]),p)) for p in os.listdir("/proc") if p.isdigit() and "multiprocessing-fork" in open("/proc/"+p+"/cmdline","rb").read().replace(b"\0",b" ").decode("utf-8","ignore")]; print(max(vals)[1]) if vals else sys.exit(1)'

# Record a flamegraph from the hottest running api worker.
profile DURATION="30":
    mkdir -p ./profiling
    pid=$(just profile-pid); echo Profiling api worker PID $pid; docker exec -u root api py-spy record --pid $pid --duration {{DURATION}} --rate 100 --idle --output /tmp/flame.svg
    docker cp api:/tmp/flame.svg ./profiling/flame-$(date -u +%Y%m%dT%H%M%SZ).svg
    ls -lh ./profiling/ | tail -1

# Live top for the hottest running api worker.
profile-top:
    pid=$(just profile-pid); echo Profiling api worker PID $pid; docker exec -u root -it api py-spy top --pid $pid --rate 100

# Per-thread stack dump at the moment of execution. Useful when something hangs.
profile-dump:
    pid=$(just profile-pid); echo Dumping api worker PID $pid; docker exec -u root api py-spy dump --pid $pid
