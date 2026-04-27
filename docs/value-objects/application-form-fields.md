# ApplicationFormFields

## Purpose

Validated collection of application form [Field](field.md) value objects.

## Business Rules

1. The collection must contain at least one field.
2. Field names must be unique.

## Possible Errors

- `InvalidApplicationFormDataError` — when the collection is empty or two fields share the same name.
