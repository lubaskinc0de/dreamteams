# Competition Errors

[← Error Reference](index.md)

| Code | HTTP Status | Description | Metadata |
|------|-------------|-------------|----------|
| `COMPETITION_NOT_FOUND` | 404 | Competition does not exist | None |
| `INVALID_COMPETITION_DATA` | 400 | Competition data fails validation (e.g. empty description, invalid team size, mismatched `team_size` / `schedule.team_formation_*` pairing) | None |

## Related

- [Competition entity](../entities/competition.md)
- [Publish Competition](../usecase/publish_competition/usecase.md)
- [Manage Competitions](../usecase/manage_competitions/usecase.md)
