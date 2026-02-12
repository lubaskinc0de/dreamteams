# Contact (Value Object)

## Purpose

Represents a contact link or external profile associated with a participant.

## Attributes

| Attribute | Type  | Description                              |
| --------- | ----- | ---------------------------------------- |
| `title`   | `str` | title of the external profile or contact |
| `url`     | `str` | URL to the external profile or contact   |

## Business Rules

1. `title` not must be empty
2. `url` must be a valid URL.
3. The contact list must not contain duplicate URLs.
