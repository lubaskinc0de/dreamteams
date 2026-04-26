# User Bans

Backend user bans are account-level blocks managed by admins. A blocked account keeps its database records, but it cannot make authenticated API calls and its public-facing content is hidden from list endpoints that should not promote blocked users.

## Admin API

### Block User

```http
POST /admin/users/{user_id}/block
```

Authentication: required. Caller must be an admin.

Request body:

```json
{
  "reason": "Policy violation"
}
```

`reason` is optional and may be `null`.

Successful response:

```http
200 OK
```

No response body is returned.

Errors:

| Code | HTTP Status | When |
|------|-------------|------|
| `UNAUTHORIZED` | 401 | Request has no valid authenticated user |
| `ACCESS_DENIED` | 403 | Authenticated caller is not an admin |
| `USER_NOT_FOUND` | 404 | Target `user_id` does not exist |
| `VALIDATION_ERROR` | 422 | Path or body shape is invalid |

### Unblock User

```http
POST /admin/users/{user_id}/unblock
```

Authentication: required. Caller must be an admin.

Request body: none.

Successful response:

```http
200 OK
```

No response body is returned.

Errors:

| Code | HTTP Status | When |
|------|-------------|------|
| `UNAUTHORIZED` | 401 | Request has no valid authenticated user |
| `ACCESS_DENIED` | 403 | Authenticated caller is not an admin |
| `USER_NOT_FOUND` | 404 | Target `user_id` does not exist |
| `VALIDATION_ERROR` | 422 | Path is invalid |

## Blocked Account Behavior

When a blocked user makes an authenticated request, the API responds:

```http
403 Forbidden
```

```json
{
  "code": "ACCOUNT_BLOCKED",
  "message": "Your account has been blocked",
  "meta": {
    "reason": "Policy violation",
    "blocked_at": "2026-04-26T19:00:00+00:00"
  }
}
```

`meta.reason` and `meta.blocked_at` may be `null` if the block has no reason or timestamp.

The block check happens during authenticated user resolution, so clients should treat `ACCOUNT_BLOCKED` as a terminal account state for the current session. After an admin unblocks the user, the same authenticated user can access endpoints again.

## List Visibility Rules

Blocked users are excluded from relevant read models:

- Competitions owned by blocked organizers are hidden from public preview/explore and organizer-facing competition reads/lists that load through the standard competition gateways.
- Applications submitted by blocked participants are hidden from organizer application lists.
- Organizer and participant role lookups return no role for blocked users, which causes role-gated endpoints to fail rather than exposing blocked account data.

These rules do not delete data. They only affect API visibility while the account remains blocked.

## Frontend Handling

Frontend clients should:

- Show a dedicated blocked-account state when any authenticated request returns `403 ACCOUNT_BLOCKED`.
- Display `meta.reason` when present.
- Avoid retry loops for `ACCOUNT_BLOCKED`; the user cannot self-resolve this state through normal authenticated endpoints.
- Clear or stop optimistic authenticated data refreshes until the user signs out or an admin unblocks the account.
