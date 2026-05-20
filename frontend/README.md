# DreamTeams Frontend

Nuxt application for the DreamTeams competition platform.

The frontend is a client-side Nuxt 4 app that sits behind the same Nginx/OAuth2-Proxy entrypoint as the backend API. It provides public competition discovery, authenticated participant and organizer workflows, admin screens, onboarding, profile management, application review, and export actions.

## What It Does

- **Public landing and discovery.** Visitors can open the home page, read product/legal pages, and browse public competition previews.
- **Authentication-aware navigation.** The app checks OAuth2 session state through `/oauth2/auth`, loads `/api/users/me`, and routes users into onboarding, profile, admin, participant, or organizer flows.
- **Onboarding.** Authenticated users without a profile choose and create a participant or organizer profile. Organizer registration uses invite codes.
- **Participant experience.** Participants manage profile data, skills, contacts, avatar, browse participant-only competition listings, submit applications, and review their own applications.
- **Organizer workspace.** Organizers create, view, edit, archive, and delete competitions; configure schedules, team formation, tracks, tags, venues, milestones, application forms, and submitted applications.
- **Application review.** Organizers inspect submitted applications, accept or reject them, and start CSV exports.
- **Admin area.** Admins manage users, block/unblock accounts, issue/revoke organizer invites, and maintain the tag catalog.
- **Account restriction handling.** Blocked-user API responses are captured globally and redirect the user to a dedicated restricted-account page.
- **Internationalization.** Russian and English locales are supported without locale prefixes in URLs.
- **Runtime configuration.** API base URL, mock mode, timeout, and retry settings can be configured through environment variables or a runtime `public/config.js` file.

## Technology Stack

- **Nuxt 4** with SPA/static generation mode (`ssr: false`)
- **Vue 3**
- **TypeScript** with Nuxt type checking enabled
- **Nuxt UI** for the component system and design tokens
- **Pinia** for feature state stores
- **Vue Router** through file-based Nuxt pages
- **Zod** for form validation schemas
- **@nuxtjs/i18n** for Russian/English localization
- **Heroicons via Iconify** for UI icons
- **Prettier** for formatting

## Application Structure

```text
frontend/
├── app/
│   ├── components/        # Reusable UI, profile, home, competition, and form components
│   ├── composables/       # API client, auth, navigation, formatting, error handling
│   ├── layouts/           # Default and onboarding layouts
│   ├── middleware/        # Global auth/onboarding/role/cookie routing rules
│   ├── pages/             # File-based routes
│   ├── plugins/           # Client startup hooks for auth and cookie consent
│   ├── schemas/           # Zod form schemas
│   ├── stores/            # Pinia stores grouped by feature
│   ├── types/             # API and UI TypeScript types
│   └── utils/             # Shared utility helpers
├── locales/               # ru/en translations
├── public/                # Static assets and runtime config.js
├── nuxt.config.ts         # Nuxt, i18n, runtime config, SEO, build settings
└── package.json           # npm scripts and dependencies
```

## Routes

Public routes:

- `/` - landing page
- `/competitions` - public competition preview listing
- `/legal/privacy-policy`, `/legal/terms-of-service`, `/legal/cookie-policy`
- `/cookies-required`
- `/account-restricted`

Authenticated routes:

- `/onboarding` - profile role selection and registration
- `/me` - current user's profile workspace
- `/explore` - participant competition exploration
- `/competitions/submit/[id]` - participant application submission
- `/me/applications` and `/me/applications/[id]` - participant application history and details

Organizer routes:

- `/me/competitions`
- `/me/competitions/create`
- `/me/competitions/[id]`
- `/me/competitions/edit/[id]`
- `/me/competitions/[id]/application-form`
- `/me/competitions/[id]/applications`
- `/me/competitions/[id]/applications/[applicationId]`

Admin routes:

- `/admin`
- `/admin/users`
- `/admin/users/[id]`
- `/admin/invites`
- `/admin/tags`
- `/register-superuser`

## Authentication Flow

The frontend does not handle credentials directly. Authentication is owned by the backend edge stack:

```text
Browser -> Nginx -> OAuth2-Proxy -> Authentik
```

Client behavior:

1. `plugins/auth.client.ts` calls `useAuth().checkAuthStatus()` on app startup.
2. `useAuth` calls `useApi().checkAuth()`, which requests `${apiBase}/oauth2/auth`.
3. If authenticated, the app fetches `${apiBase}/api/users/me`.
4. The result determines whether the user has a profile, needs onboarding, is an admin, is a participant, is an organizer, or is blocked.
5. `middleware/auth.global.ts` redirects unauthenticated users away from protected routes, sends users without a profile to onboarding, blocks non-admin access to `/admin`, and restricts `/explore` to participants.
6. Login redirects to `${apiBase}/oauth2/sign_in?rd=...`.
7. Logout goes through `/logout`, which lets Nginx/OAuth2-Proxy/Authentik clear the full session chain.

The frontend trusts structured backend errors. If an API response contains `ACCOUNT_BLOCKED`, `useBlockedAccount` stores the restriction state and routes the user to `/account-restricted`.

## API Client

`app/composables/useApi.ts` is the single API boundary for the app.

It provides:

- typed methods for users, organizers, participants, competitions, application forms, applications, invites, tags, admin users, and exports;
- structured `ApiError` handling from backend error responses;
- request timeout support;
- exponential backoff with jitter for transient network errors, `429`, and `5xx` responses;
- mock API fallback when mock mode is enabled;
- account-blocked interception before outgoing requests.

The client reads runtime settings from `useRuntimePublicConfig()`, which merges Nuxt public runtime config with optional `window.__DREAMTEAMS_CONFIG__` from `/config.js`. This allows the same static frontend build to be deployed with different API endpoints.

## State Management

Pinia stores are grouped by product area:

- `user` - current profile, roles, admin/organizer/participant flags
- `participant` and `organizer` - registration and profile updates
- `competition` - organizer-owned competition list, detail, creation, update, archive, delete
- `applicationForm` - form creation, read, delete
- `competitionApplications` - organizer review list, status filtering, export polling
- `myApplications` - participant submissions and application history
- `invites` - admin organizer invite lifecycle
- `adminUsers` - admin user listing, details, block/unblock
- `adminTags` - admin tag catalog management
- `notifications` - local notification/toast state

Stores keep API calls out of page components and centralize loading, error, success, and refresh behavior.

## Forms and Validation

Zod schemas under `app/schemas/` validate user input before requests reach the backend:

- `participant.ts` - participant profile fields, age, contacts, skills, participant type
- `organizer.ts` - organizer profile and registration fields
- `competition.ts` - competition creation/editing, schedule, team formation, participant limits, tracks, tags, venue, milestones, archive status

Validation mirrors key backend invariants where useful for UX. For example, team competitions require matching team formation dates and team-size data, registration periods must be coherent, milestones must not duplicate timestamps, and participant/profile fields observe length and format constraints.

Backend validation remains authoritative. Frontend validation exists to give fast feedback and reduce avoidable round trips.

## Internationalization

The app uses `@nuxtjs/i18n` with:

- default locale `ru`;
- supported locales `ru` and `en`;
- translation files in `frontend/locales/`;
- `strategy: "no_prefix"`, so language choice is stored in a cookie instead of changing route paths;
- localized number and datetime formats in `app/i18n.config.ts`.

Use translation keys for visible UI text. Avoid hardcoding user-facing strings in components unless they are temporary development-only labels.

## Runtime Configuration

Environment variables:

```env
NUXT_PUBLIC_API_BASE=http://localhost
NUXT_PUBLIC_USE_MOCK=false
NUXT_PUBLIC_API_TIMEOUT=10000
NUXT_PUBLIC_API_MAX_RETRIES=3
NUXT_PUBLIC_API_RETRY_BASE_DELAY=300
NUXT_PUBLIC_API_RETRY_MAX_DELAY=10000
```

At runtime, `/config.js` may define:

```js
window.__DREAMTEAMS_CONFIG__ = {
  apiBase: "https://dreamteams.example",
  useMock: "false",
  apiTimeout: 10000,
  apiMaxRetries: 3,
  apiRetryBaseDelay: 300,
  apiRetryMaxDelay: 10000
}
```

Values from `window.__DREAMTEAMS_CONFIG__` override Nuxt public runtime config in the browser.

## Development

Install dependencies:

```bash
npm install
```

Run dev server:

```bash
npm run dev
```

Build production app:

```bash
npm run build
```

Generate static output:

```bash
npm run generate
```

Preview production build:

```bash
npm run preview
```

From the repository root, the main shortcuts are:

```bash
just dev-environment  # install backend dev deps and frontend npm deps
just build-frontend   # cd frontend && npm run generate
just up               # run frontend behind Nginx with the full local stack
```

## Quality

- Keep components focused on rendering and local interaction.
- Put API calls in `useApi` and feature stores, not directly in deeply nested components.
- Put shared formatting in composables such as `useCompetitionFormatters` and `useCompetitionStatus`.
- Keep form invariants in Zod schemas and backend-aligned TypeScript types.
- Use Nuxt UI components and existing design tokens before introducing custom styling.
- Keep visible text in locale files.
- Preserve the auth middleware rules when adding new protected routes.
- For new backend endpoints, update `types/api.ts`, `useApi.ts`, the relevant store, and the page/component flow together.

## Deployment Model

The frontend is built as a static Nuxt app and served behind Nginx. In local Docker Compose, the frontend dev server runs in a Node container and Nginx proxies public traffic to it. In image builds, `frontend/Dockerfile` builds the frontend image separately from the backend image.

The frontend should call the public Nginx/API base URL, not internal container names. Nginx is responsible for routing:

- `/` to the frontend;
- `/oauth2/*` to OAuth2-Proxy;
- `/api/*` to the main API;
- `/api/exports/*` to the exporter API;
- `/s3/*` to S3-compatible object storage.
