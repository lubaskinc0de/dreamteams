# Authentik local setup

DreamTeams uses [Authentik](https://docs.goauthentik.io/) as the OIDC provider for `oauth2-proxy`. Authentik runs as docker services inside the compose stack. The OAuth2 provider and application are configured manually through the Authentik admin UI on first boot.

## Architecture recap

```
Browser  -> nginx:80 -> oauth2-proxy:8000 -> OIDC discovery -> Authentik
Browser  -> 127.0.0.1.sslip.io:8080 -> authentik-server:9000
```

- `127.0.0.1.sslip.io` is a public DNS wildcard that resolves to `127.0.0.1`.
- Authentik uses the shared `db` postgres container with its own `authentik` role and database, created by `.config/init-db.sql`.
- `oauth2-proxy` keeps handling `/oauth2/*`, cookie storage in Redis, and header injection into the DreamTeams app.

## First-boot setup

### 1. Start the stack

```bash
just clear-all      # needed once so postgres initdb creates the Authentik role + DB
just up-silent
```

`authentik-server` and `authentik-worker` will start. `oauth2-proxy` may fail until you create the OIDC provider and set a real client secret in `docker/docker-compose.yml`.

### 2. Complete Authentik initial setup

Open `http://127.0.0.1.sslip.io:8080/if/flow/initial-setup/`.

The setup flow creates the default admin user:

- Username: `akadmin`
- Password: choose one during setup

After that, the admin UI is available at `http://127.0.0.1.sslip.io:8080/if/admin/`.

### 2. Create the OAuth2 / OIDC provider

1. Open Authentik admin.
2. Go to **Applications** -> **Providers** -> **Create**.
3. Choose **OAuth2/OpenID Provider**.
4. Set:
   - Name: `DreamTeams OAuth2 Proxy`
   - Authorization flow: the default authentication flow
   - Client type: `Confidential`
   - Client ID: `dreamteams-oauth2-proxy`
   - Redirect URIs: `http://localhost/oauth2/callback`
   - Scopes: `openid`, `email`, `profile`, `offline_access`
5. Save and copy the generated client secret.

### 3. Create the application

1. Go to **Applications** -> **Applications** -> **Create**.
2. Set:
   - Name: `DreamTeams`
   - Slug: `dreamteams`
   - Provider: the provider you just created
3. Save.

The issuer URL for `oauth2-proxy` will then be:

```text
http://127.0.0.1.sslip.io:8080/application/o/dreamteams/
```

### 4. Paste credentials into oauth2-proxy

Edit the `oauth2-proxy` service environment in `docker/docker-compose.yml` and set the client secret:

```yaml
OAUTH2_PROXY_CLIENT_ID: dreamteams-oauth2-proxy
OAUTH2_PROXY_CLIENT_SECRET: <paste generated client secret>
```

`OAUTH2_PROXY_COOKIE_SECRET` can stay as-is unless you want to rotate it.

### 5. Configure RP-initiated logout to end the Authentik session

By default, app-initiated logout only invalidates the provider session. To make `/logout` also end the Authentik session:

1. Open **Flows and Stages** -> **Flows**.
2. Open `default-provider-invalidation-flow`.
3. Add the `default-invalidation-logout` stage to that flow.

This matches Authentik's documented behavior for full logout from an OIDC relying party.

### 6. Restart oauth2-proxy and verify discovery

```bash
docker compose -f docker/docker-compose.yml restart oauth2-proxy
```

Then check:

- Discovery URL: `http://127.0.0.1.sslip.io:8080/application/o/dreamteams/.well-known/openid-configuration`
- Unauthenticated probe: `http://localhost/oauth2/auth` should return `401`
- After login through the browser, `http://localhost/oauth2/auth` should return `202`

## Notes

- This is a local-dev replacement, not an identity migration. Existing local app users and old provider identities are expected to be discarded.
- Normal `just clear` resets only the app schema in the `postgres` database. Authentik data survives there; `just clear-all` removes the whole local stack state.
