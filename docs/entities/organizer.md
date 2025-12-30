# Organizer

## Purpose

Represents an organization that hosts hackathons and competitions on the platform.

## Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `id` | `OrganizerId` (UUID) | Organizer identifier |
| `user_id` | `UserId` (UUID) | Reference to user account |
| `organizer_name` | `str` | Organization name |
| `phone_number` | `str` | Contact phone number |
| `contact_email` | `str` | Contact email address |
| `logo` | `Logo \| None` | Organization logo URL |

## Business Rules

1. Combination of `phone_number` and `contact_email` must be unique across all organizers
2. Each organizer must be linked to exactly one user via `user_id`
3. Organizer name must not exceed 70 characters
4. Phone number must follow Russian format

## Relationships

```
Organizer 1 ──> 1 User
```

- Each organizer belongs to exactly one user
