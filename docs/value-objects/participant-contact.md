# Contact (Value Object)

## Purpose

Represents a contact link or external profile associated with a participant.

## Attributes

| Attribute | Type  | Description                            |
| --------- | ----- | -------------------------------------- |
| `url`     | `str` | URL to the external profile or contact |

## Business Rules

1. `url` must be a valid URL.
2. The contact list must not contain duplicate URLs.
