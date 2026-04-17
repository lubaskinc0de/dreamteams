# UpdateOrganizer

## Purpose

Updates the organizer profile of the currently authenticated user.

## Input

| Field            | Type       | Required | Description |
|------------------|------------|----------|-------------|
| `organizer_name` | `str`      | Yes      | Organizer display name (max 70 characters) |
| `contact_email`  | `EmailStr` | Yes      | Organizer contact email |

## Output

No output. Operation succeeds or raises error.

## Business Rules

1. `contact_email` must be unique across all organizers (unless it is the organizer's current email)

## Errors

| Error Code | HTTP Status | Condition |
|-----------|-------------|-----------|
| `ORGANIZER_NOT_FOUND` | 404 | Authenticated user has no organizer role |
| `ORGANIZER_ALREADY_EXISTS` | 409 | Another organizer already uses this contact email |
| `UNAUTHORIZED` | 401 | User is not authenticated |
