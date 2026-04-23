# ZITADEL local setup

DreamTeams uses [ZITADEL](https://zitadel.com) as the OIDC provider for oauth2-proxy. ZITADEL runs as a docker service inside the compose stack. The project + OIDC application are configured manually through the ZITADEL console on first boot — this page walks through the steps.

## Architecture recap

```
Browser  ──► nginx:80 ──► oauth2-proxy:8000 ──► OIDC discovery ──┐
                                                                 │
Browser  ──► 127.0.0.1.sslip.io:8080 ──► zitadel-proxy (nginx)   │
                                             │                   │
                                             ├─ /ui/v2/login ──► zitadel-login:3000 (Next.js)
                                             └─ /*           ──► zitadel-api:8080 (Go, h2c)
```

- `127.0.0.1.sslip.io` is a public DNS wildcard that resolves to `127.0.0.1`. The browser reaches the proxy directly; the oauth2-proxy container reaches it via the `host-gateway` extra_hosts entry → docker-published port 8080 → `zitadel-proxy`.
- ZITADEL v4 splits the login UI into its own service (`zitadel-login`, Next.js) and the API (`zitadel-api`, Go) is HTTP/2 cleartext — `zitadel-proxy` (nginx) fronts both: `proxy_pass` for the login UI and `grpc_pass` for the API.
- ZITADEL shares the existing `db` postgres container (its own `zitadel` role + database, created by `.config/init-db.sql`). It bypasses pgbouncer.

## First-boot setup

### 1. Start the stack

```bash
just clear          # only needed once, to force postgres initdb to pick up the ZITADEL role + DB
just up-silent
```

`zitadel-api` runs its init + setup + start in one process (`start-from-init`), then `zitadel-login` and `zitadel-proxy` come up. `oauth2-proxy` will fail to start — this is expected, it has empty client credentials. You'll fix that in step 4.

### 1. Log into the ZITADEL console

Open `http://127.0.0.1.sslip.io:8080/ui/console` and sign in:

- Username: `zitadel-admin@zitadel.127.0.0.1.sslip.io`
- Password: `Password1!`

`ZITADEL_FIRSTINSTANCE_ORG_HUMAN_PASSWORDCHANGEREQUIRED=false` is set in `.config/.env.zitadel`, so no forced password reset on first login.

### 3. Create a project + OIDC application

1. Left nav → **Projects** → **Create New Project**. Name it `dreamteams`.
2. Inside the project → **New** (application) → choose **WEB**.
3. Name: `dreamteams-oauth2-proxy`.
4. Authentication Method: **PKCE**
5. Redirect URIs: `http://localhost/oauth2/callback`
6. Post Logout URIs: `http://localhost/`
7. Finish the wizard. ZITADEL will show the generated **Client ID**.

### 4. Paste credentials into oauth2-proxy

Edit `.config/.env.oauthproxy`:

```ini
OAUTH2_PROXY_CLIENT_ID=<paste client id>
```