# Use Case: Manage Applications

**Actor**: Organizer
**Module**: `application.manage_applications`

## Goal

An organizer reviews and processes applications submitted to their competitions: read a single application, browse the applicant list, accept participants, and reject those who do not meet the criteria.

## Interactors

- [ReadApplication](./read_application.md) — read a single application
- [ListApplicationsByCompetition](./list_applications.md) — list all applications for a competition
- [AcceptApplication](./accept_application.md) — approve a pending application
- [RejectApplication](./reject_application.md) — reject a pending application
