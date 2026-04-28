# Invite Errors

[← Error Reference](index.md)

| Code | HTTP Status | Description | Metadata |
|------|-------------|-------------|----------|
| `INVITE_NOT_FOUND` | 404 | Invite with given ID or code does not exist | None |
| `INVITE_ALREADY_REVOKED` | 403 / 409 | Invite has been revoked and cannot be used (403) or revoked again (409) | None |
| `INVITE_ALREADY_USED` | 409 | Invite has already been used for registration | None |

## Related

- [OrganizerInvite entity](../entities/organizer-invite.md)
- [Issue Invite use cases](../usecase/issue_invite/usecase.md)
- [View Issued Invites use cases](../usecase/view_issued_invites/usecase.md)
- [Register Organizer](../usecase/register_user/register_organizer.md)
