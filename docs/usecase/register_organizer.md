# RegisterOrganizer

## Purpose

Creates a new user and attaches organizer role to the user.

## Input

| Field | Type | Description |
|-------|------|-------------|
| `organizer_name` | `str` | Organization name |
| `phone_number` | `str` | Contact phone number |
| `contact_email` | `str` | Contact email address |

## Output

| Field | Type | Description |
|-------|------|-------------|
| `organizer_id` | `OrganizerId` | Created organizer identifier |
| `user_id` | `UserId` | Created user identifier |

## Business Rules

1. Phone number and email combination must be unique
2. If user with given `auth_user_id` does not exist, create new user
3. If user with given `auth_user_id` exists, use existing user
4. Logo is set to `None` on registration
5. User can have only one organizer role

## Flow

1. Check uniqueness of phone number and email via `OrganizerGateway`
2. Get or create user via `UserFactory`
3. Generate new `organizer_id`
4. Create `Organizer` entity
5. Attach organizer to user via `user.attach_organizer()`
6. Save organizer via `UoW`
7. Return created organizer and user identifiers

## Error Cases

- `OrganizerAlreadyExistsError` — phone or email already registered
- `UserAlreadyOrganizerError` — user already has organizer role
