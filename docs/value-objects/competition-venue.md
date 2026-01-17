# CompetitionVenue

## Purpose

Defines competition format and location.

## Type

Value object (dataclass)

## Fields

| Field | Type | Description |
|-------|------|-------------|
| `format` | `CompetitionFormat` | Competition format (ONLINE, OFFLINE, HYBRID) |
| `location` | `str \| None` | Physical location (required for OFFLINE and HYBRID) |

## Validation Rules

1. Location is required and must not be empty for OFFLINE and HYBRID formats
2. Location is optional for ONLINE format

## Possible Errors

- `InvalidCompetitionDataError` — when location is missing for OFFLINE or HYBRID format
