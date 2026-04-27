# Contact (Value Object)

## Purpose

Represents a participant contact entry. The value is an arbitrary string such as a URL, handle, phone number, or email address.

## Attributes

| Attribute | Type  | Description                              |
| --------- | ----- | ---------------------------------------- |
| `title`   | `str` | Title of the external profile or contact |
| `value`   | `str` | Contact value (URL, handle, phone, email, etc.) |

## Business Rules

1. Non-empty `title` validation happens at the application boundary.
2. Contact collection uniqueness is owned by [`ParticipantContacts`](participant-contacts.md).
