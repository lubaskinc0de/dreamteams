# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Nuxt 4** frontend application for "DreamTeams" - an IT competition aggregator platform that helps users find teammates and organizers manage events. The app is built as a **SPA (ssr: false)** with OAuth2 authentication via backend proxy.

**Key Technical Stack:**
- Nuxt 4 (Vue 3, TypeScript strict mode)
- NuxtUI (Tailwind CSS based component library)
- Pinia (state management)
- Vue I18n (internationalization - Russian/English)
- Zod (schema validation)

## Development Commands

```bash
# Install dependencies
npm install

# Development server (http://localhost:3000)
npm run dev

# Type checking (strict mode enabled)
npm run build

# Preview production build
npm run preview

# Generate static site
npm run generate
```

## Environment Configuration

Create `.env` from `.env.example`:

```env
NUXT_PUBLIC_API_BASE=http://localhost:8000
NUXT_PUBLIC_USE_MOCK=true  # Set to 'false' for real API
```

- **Mock Mode**: When `NUXT_PUBLIC_USE_MOCK=true`, the app uses `useMockApi()` instead of real backend calls
- **Real API**: When `false`, uses `NUXT_PUBLIC_API_BASE` for OAuth2 and API endpoints

## Architecture

### Authentication Flow

The app implements a **three-state authentication model**:

1. **Unauthenticated** - user not logged in via OAuth2
2. **Authenticated, needs onboarding** - logged in via Authentik but no profile/organizer created
3. **Authenticated, has profile** - fully onboarded user

**Flow Implementation:**
- `app/plugins/auth.client.ts` - runs on app start, calls `checkAuthStatus()`
- `app/middleware/auth.global.ts` - runs on every route, enforces redirects:
  - Unauthenticated + protected route → 401 error page
  - Authenticated + needs onboarding → redirect to `/onboarding`
  - Authenticated + has profile + home → redirect to `/profile`
- `app/composables/useAuth.ts` - manages auth state via `useState()`:
  - `isAuthenticated` - OAuth2 check via `/oauth2/auth`
  - `needsOnboarding` - true if authenticated but profile fetch returns 401/404/USER_HAS_NO_ROLE
  - `hasProfile` - true if profile exists with valid data

**OAuth2 Endpoints** (handled by backend):
- `/oauth2/sign_in?rd=<redirect>` - login
- `/oauth2/sign_out?rd=<redirect>` - logout
- `/oauth2/auth` - check authentication status

### API Client Pattern

**Location**: `app/composables/useApi.ts`

Returns different implementations based on `NUXT_PUBLIC_USE_MOCK`:
- `true` → `useMockApi()` (simulated responses, delays, validation)
- `false` → real API client using `$fetch`

**Error Handling**: All API methods return `{ data, error }` shape:
```typescript
const { data, error } = await api.getUserProfile();
if (error) {
  // error: { code: string, message: string, meta: object | null }
}
```

**Error Codes** (from `app/types/api.ts`):
- `VALIDATION_ERROR` (422)
- `UNAUTHORIZED` (401)
- `AUTH_USER_ALREADY_EXISTS` (409)
- `ORGANIZER_ALREADY_EXISTS` (409)
- `USER_NOT_FOUND` (404)
- `USER_HAS_NO_ROLE` (404)
- `ACCESS_DENIED` (403)
- `INTERNAL_SERVER_ERROR` (500)

### State Management (Pinia)

**Stores**:
- `app/stores/user.ts` - user profile state, `isOrganizer` getter
- `app/stores/organizer.ts` - organizer registration flow, auto-refreshes user profile on success

**Pattern**: Stores call `useApi()` composable, handle loading/error states, and update reactive state.

### Form Validation

**Schema Location**: `app/schemas/organizer.ts`

Uses **Zod** with i18n integration via factory pattern:
```typescript
const { organizerRegistrationSchema } = createOrganizerSchemas(t);
```

**Phone Validation**: Russian format only - `PHONE_REGEX = /^\+7\d{10}$/`

**Organizer Name**: Max 70 characters, trimmed on submit

### Internationalization (i18n)

**Configuration**:
- `nuxt.config.ts` - defines locales, strategy `no_prefix` (language in cookie only)
- `i18n.config.ts` - number/date formats for RU/EN
- `locales/ru.json` & `locales/en.json` - translations

**Usage**: Access via `$t()` in components or `const { $i18n } = useNuxtApp()` in composables.

**Default Locale**: Russian (`ru`)

### Routing & Pages

**Protected Routes** (require authentication):
- `/profile` - user profile/dashboard
- `/onboarding` - organizer registration
- `/me` - (legacy/alternative profile route)
- `/start` - (onboarding alternative)

**Public Routes**:
- `/` - home/landing page

**Layouts**:
- `app/layouts/default.vue` - standard layout with navigation
- `app/layouts/onboarding.vue` - minimal layout for registration flow

### Component Organization

**Key Components**:
- `app/components/OrganizerRegistrationForm.vue` - Zod-validated form with real-time validation
- `app/components/LanguageSwitcher.vue` - i18n language toggle
- `app/components/ThemeToggle.vue` - dark/light mode toggle

**Composables** (reusable logic):
- `useApi()` - API client
- `useAuth()` - authentication state/actions
- `useErrorHandler()` - centralized error handling
- `useNavigation()` - navigation helpers
- `useOnboarding()` - onboarding flow state
- `useTheme()` - theme management

### NuxtUI Theming

**Configuration**: `app.config.ts`

Defines custom:
- Primary color: blue
- Gray scale: slate
- Custom animations, spacing utilities
- Semantic color tokens for theming
- Icon mappings (using `heroicons`)

**Pattern**: Use semantic tokens like `text-primary-400` instead of direct Tailwind classes.

### Prerendering

**Static Generation** (`nuxt.config.ts`):
```typescript
nitro: {
  prerender: {
    routes: ['/'],  // Only home page prerendered
    ignore: ['/profile', '/onboarding', '/me', '/start'],  // Protected routes
  }
}
```

## Important Patterns

### Type Safety
- **Strict mode enabled**: All TypeScript errors must be resolved
- **API types**: Defined in `app/types/api.ts`
- **UI types**: Defined in `app/types/ui.ts`

### Error Pages
- `app/error.vue` - custom error page with i18n support
- Displays appropriate messages for 401, 404, 500 errors

### useState() for Auth
Authentication state uses `useState()` to persist across navigation without prop drilling:
```typescript
const isAuthenticated = useState<boolean>('auth-isAuthenticated', () => false);
```

### Toast Notifications
Use `useToast()` from NuxtUI for user feedback. Example in `organizer.ts` store after registration success.

### Build
always run build after new changes to ensure they work correctly

## When Adding Features

1. **New API endpoint**: Add to `useApi()` and `useMockApi()`, define types in `app/types/api.ts`
2. **New form**: Create Zod schema in `app/schemas/`, add i18n strings to `locales/`
3. **New protected route**: Add to `protectedRoutes` array in `app/middleware/auth.global.ts`
4. **New store**: Follow Pinia options API pattern, call `useApi()` in actions
5. **New page**: Add to `app/pages/`, Nuxt auto-generates routes

## Common Gotchas

- **SPA mode**: No SSR, all auth checks happen client-side
- **Mock vs Real API**: Toggle via `.env`, both implementations must match signatures
- **Phone format**: Only Russian `+7XXXXXXXXXX` supported
- **i18n factory pattern**: Schemas use `createOrganizerSchemas(t)` to access translations at runtime
- **Global middleware**: Runs on every navigation, waits for auth loading state
