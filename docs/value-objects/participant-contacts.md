# ParticipantContacts

## Purpose

Validated collection of participant [ParticipantContact](participant-contact.md) value objects.

## Business Rules

1. Empty collections are allowed.
2. Contact titles must be unique.
3. Contact values must be unique.

## Possible Errors

- `InvalidParticipantDataError` — when two contacts share the same title or value.
