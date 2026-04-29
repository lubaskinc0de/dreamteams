# RegisterSuperuser

## Purpose

Creates a new user with `is_admin = True` (superuser). The caller must supply a
password that matches the hash stored in the application configuration. The created user has no roles attached.

## Input

| Field | Type | Description |
|-------|------|-------------|
| `password` | `str` | Plain-text password to verify against the configured hash |

## Output

| Field | Type | Description |
|-------|------|-------------|
| `user_id` | `UserId` | Created user identifier |

## Business Rules

1. The supplied `password` is verified against hash stored in the application configuration
2. If the password does not match, registration is rejected with
   `INVALID_SUPERUSER_PASSWORD`
3. If user with the given `auth_user_id` does not exist, create new user
4. If user with the given `auth_user_id` already exists, reject with
   `USER_ALREADY_EXISTS`
5. The created user has `is_admin = True` and no roles

## Errors

| Error Code | HTTP Status | Condition |
|-----------|-------------|-----------|
| `INVALID_SUPERUSER_PASSWORD` | 403 | Supplied password does not match the configured hash |
| `AUTH_USER_ALREADY_EXISTS` | 409 | User with given `auth_user_id` is already registered |
