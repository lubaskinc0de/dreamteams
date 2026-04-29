# CompetitionTag

## Purpose

Represents a catalog tag used for quick competition search and filtering.

## Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `id` | `CompetitionTagId` (UUID) | Tag identifier |
| `value` | `str` | Human-readable tag value, for example `Python` or `Backend` |

## Business Rules

1. Tag value is trimmed and must not be empty.
2. Tag values are unique case-insensitively in the database.
3. Administrators manage the tag catalog.
4. Organizers attach existing tags to competitions by ID.
