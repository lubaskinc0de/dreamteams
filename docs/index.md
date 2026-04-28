# DreamTeams

**DreamTeams** is a competition management platform for organizing and participating in hackathons and olympiads. It connects organizers who create events with participants who want to find teams and compete.

---

## Architecture Overview

The platform follows strict **Clean Architecture** with five layers enforced by import-linter:

| Layer | Purpose |
|-------|---------|
| **Entities** | Core domain models: [User](entities/user.md), [Organizer](entities/organizer.md), [Competition](entities/competition.md), [CompetitionTag](entities/competition-tag.md), [Application](entities/application.md) |
| **Value Objects** | Core value objects and validated collections: [CompetitionTrack](value-objects/competition-track.md), [CompetitionTracks](value-objects/competition-tracks.md), [CompetitionTags](value-objects/competition-tags.md), [CompetitionSchedule](value-objects/competition-schedule.md), [ApplicationFormFields](value-objects/application-form-fields.md) |
| **Application** | Use cases (interactors) and gateway interfaces |
| **Adapters** | Database gateways, SQLAlchemy models, auth providers |
| **Presentation** | FastAPI routers and request/response models |

---

## Actors

| Actor | Description |
|-------|-------------|
| **Visitor** | Unauthenticated user — can browse public competition listings |
| **Organizer** | Registered organization — creates and manages competitions, reviews applications |
| **Participant** | Individual user — submits applications to competitions |
| **Admin** | Superuser — manages organizer invites and platform administration |

---

## Public API Notes

- [User Bans](user-bans.md) — admin block/unblock endpoints, blocked-account errors, and public visibility behavior

---

## Core Flows

### Organizer Registration

1. Admin [issues an invite](usecase/issue_invite/issue_invite.md) with a unique code
2. Visitor [registers as organizer](usecase/register_user/register_organizer.md) using the invite code
3. Organizer [publishes a competition](usecase/publish_competition/publish_competition.md)
4. Organizer optionally [creates an application form](usecase/manage_application_form/create_application_form.md) for the competition

### Participant Flow

1. Visitor [registers as participant](usecase/register_user/register_participant.md)
2. Participant [browses competitions](usecase/submit_application/list_competitions.md)
3. Participant [submits an application](usecase/submit_application/submit_application.md) to a competition
4. Organizer [accepts or rejects](usecase/review_application/usecase.md) the application
5. Participant can [withdraw](usecase/submit_application/withdraw_application.md) a pending application

---

## Entities

- [User](entities/user.md) — base account, holds organizer/participant roles
- [Organizer](entities/organizer.md) — organization profile linked to a User
- [Participant](entities/participant.md) — individual profile linked to a User
- [Competition](entities/competition.md) — hackathon or olympiad event
- [CompetitionTag](entities/competition-tag.md) — searchable tag catalog entry for competition discovery
- [Application](entities/application.md) — participant's application to a competition
- [ApplicationForm](entities/application-form.md) — optional extra fields for an application
- [OrganizerInvite](entities/organizer-invite.md) — invite code for organizer registration

---

## Use Cases

| Module | Actor | Actions |
|--------|-------|---------|
| [Register User](usecase/register_user/usecase.md) | Visitor | Register organizer, participant, or superuser |
| [Manage Profile](usecase/manage_profile/usecase.md) | User | Read, update, and delete own profile |
| [Attach Avatar](usecase/attach_avatar/usecase.md) | User | Attach or detach own profile avatar |
| [Block User](usecase/block_user/usecase.md) | Admin | Block and unblock user accounts |
| [View Users](usecase/view_users/usecase.md) | Admin | List and read platform users |
| [Issue Invite](usecase/issue_invite/usecase.md) | Admin | Issue, inspect, and revoke organizer invites |
| [View Issued Invites](usecase/view_issued_invites/usecase.md) | Admin | List invites issued by the admin |
| [Manage Tags](usecase/manage_tags/usecase.md) | Admin | Create, read, list, delete competition tags |
| [View Tags](usecase/view_tags/usecase.md) | Participant/Organizer | Search and list available competition tags |
| [Publish Competition](usecase/publish_competition/usecase.md) | Organizer | Create and publish competition |
| [View My Competitions](usecase/view_my_competitions/usecase.md) | Organizer | List and read owned competitions |
| [Update My Competition](usecase/update_my_competition/usecase.md) | Organizer | Update general info, schedule, and archive status |
| [Delete Competition](usecase/delete_competition/usecase.md) | Organizer | Delete owned competition |
| [Preview Competitions](usecase/preview_competitions/usecase.md) | Visitor | Browse public competition listings |
| [Manage Application Form](usecase/manage_application_form/usecase.md) | Organizer | Create, read, delete application forms |
| [Submit Application](usecase/submit_application/usecase.md) | Participant | Explore competitions, apply, and withdraw pending application |
| [View My Applications](usecase/view_my_applications/usecase.md) | Participant | List and read own applications |
| [View Submitted Applications](usecase/view_submitted_applications/usecase.md) | Organizer | List applications submitted to an owned competition |
| [Review Application](usecase/review_application/usecase.md) | Organizer | Read, accept, and reject applications |

---

## Error Reference

All API errors follow a standardized format. See the [Error Reference](errors/index.md) for the full list of error codes by category:

- [Authentication & Authorization](errors/auth.md)
- [User & Organizer](errors/user-management.md)
- [Invites](errors/invite-management.md)
- [Competitions](errors/competition-management.md)
- [Applications](errors/application-management.md)
- [Participants & Media](errors/participant-media.md)
- [Generic](errors/generic.md)
- [Exporter](exporter/errors.md)

---

## Bounded Contexts

- [Exporter](exporter/index.md) — the CSV export service. Lives in `src/dreamteams_exporter/` as a sibling package; communicates with the main context over the wire, never via Python imports.
