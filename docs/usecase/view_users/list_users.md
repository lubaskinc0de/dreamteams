# ListUsers

## Purpose

Returns a paginated list of users for the admin interface. The list is designed for scanning account status and quickly finding organizer or participant profiles.

## Input

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| `page` | `int` | Page number for pagination | Positive integer |
| `search` | `str \| None` | Search by organizer name, participant full name, or user ID when the value is a UUID | Optional |
| `is_admin` | `bool \| None` | Filter by admin flag | Optional |
| `is_blocked` | `bool \| None` | Filter by ban status | Optional |
| `role` | `str \| None` | Filter by assigned role | One of `organizer`, `participant` |

## Output

| Field | Type | Description |
|-------|------|-------------|
| `items` | `list[AdminUserListItem]` | List of users |
| `total` | `int` | Total number of users matching filters |
| `page` | `int` | Current page number |

### AdminUserListItem

| Field | Type | Description |
|-------|------|-------------|
| `id` | `UserId` | User identifier |
| `is_admin` | `bool` | Whether the user has admin privileges |
| `ban_status` | `BanStatusModel` | Account ban state |
| `organizer_name` | `str \| None` | Organizer name if the user has an organizer role |
| `participant_full_name` | `str \| None` | Participant full name if the user has a participant role |

### BanStatusModel

| Field | Type | Description |
|-------|------|-------------|
| `is_blocked` | `bool` | Whether the account is banned |
| `reason` | `str \| None` | Ban reason if present |
| `blocked_at` | `datetime \| None` | Ban timestamp if present |

## Business Rules

1. Only admin users (`User.is_admin = True`) can list users
2. Returns users regardless of ban state unless `is_blocked` is provided
3. Returns users with organizer or participant roles
4. Returns empty `items` if no users match the filters
5. Search is case-insensitive for organizer and participant names
6. Pagination uses the same response shape as other list interactors

## Errors

| Error Code | HTTP Status | Condition |
|-----------|-------------|-----------|
| `USER_NOT_FOUND` | 404 | Authenticated admin user does not exist |
| `ACCESS_DENIED` | 403 | Authenticated user is not an admin |
| `VALIDATION_ERROR` | 422 | Input filters have invalid shape or values |
