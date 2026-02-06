# User

## Purpose

Represents a user in the system. Acts as a container for user roles (organizer, participant).

## Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `id` | `UserId` (UUID) | User identifier |
| `organizer` | `Organizer \| None` | Organizer role attached to user |

## Business Rules

1. User SHOULD have `Organizer` OR `Participant` role
2. When attaching organizer role, `<role>.user_id` must equal `user.id`

## Relationships

```
User 1 ──> 0..1 Organizer
```

- One user can have zero or one organizer role
