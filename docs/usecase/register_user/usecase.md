# Use Case: Register User

**Actor**: Visitor
**Module**: `application.register_user`

## Goal

Visitors register in the system. Organizers register to create competitions;
participants register to submit applications; superusers register to gain admin access.

## Interactors

- [RegisterOrganizer](./register_organizer.md) — register new organizer
- [RegisterParticipant](./register_participant.md) — register new participant
- [RegisterSuperuser](./register_superuser.md) — register new superuser (admin)
