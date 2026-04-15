# Application (Registration Application)

## Purpose

Represents a Participant's intention to participate in a specific Competition. An application captures the domains the participant wants to contribute in and goes through a review lifecycle (or is auto-accepted based on competition settings).

## Attributes

| Attribute          | Type                     | Description                                                        |
| ------------------ | ------------------------ | ------------------------------------------------------------------ |
| `id`               | `ApplicationId` (UUID)   | Unique application identifier                                      |
| `participant_id`   | `ParticipantId` (UUID)   | Reference to the applying [Participant](participant.md)                              |
| `competition_id`   | `CompetitionId` (UUID)   | Reference to the target [Competition](competition.md)                                |
| `domains`          | `list[`[`Domain`](../value-objects/domain.md)`]`           | Domains the participant wants to work in (subset of competition's) |
| `status`           | [`ApplicationStatus`](#applicationstatus-enum)      | Current status of the application                                  |
| `created_at`       | `datetime`               | Timestamp of application creation                                  |
| `form_data`        | `dict[str, Any] \| None` | Answers to the competition's ApplicationForm fields; `None` if the competition has no form |

## ApplicationStatus (Enum)

| Value      | Description                                            |
| ---------- | ------------------------------------------------------ |
| `PENDING`  | Application submitted, awaiting organizer review       |
| `ACCEPTED` | Application approved by organizer (or auto-accepted)   |
| `REJECTED` | Application rejected by organizer                      |

## Business Rules

1. `domains` list must contain at least one domain.
2. Every domain in `domains` must exist in the target `Competition.domains` (strict subset check).
3. The applying user must have an associated `Participant` profile; otherwise, access is denied.
4. A participant can have at most **one** application per competition (uniqueness constraint on `participant_id` + `competition_id`).
5. Only applications in `PENDING` status can be accepted or rejected by the organizer.
6. Only applications in `PENDING` status can be withdrawn (deleted) by the participant.
7. Only the organizer who owns the competition can accept or reject applications.
8. If the competition has `auto_accept=True`, the application is created with status `ACCEPTED`; otherwise `PENDING`.
9. If the competition has an ApplicationForm, `form_data` must be provided and validated against the form (see [ApplicationForm](./application-form.md)).
10. If the competition has no ApplicationForm, `form_data` must be `None`.

## Lifecycle

```
                          ┌─────────────────────────┐
                          │   Participant submits    │
                          │       application        │
                          └────────────┬─────────────┘
                                       │
                          ┌────────────▼─────────────┐
                          │   auto_accept = True?    │
                          └─────┬──────────────┬─────┘
                            Yes │              │ No
                    ┌───────────▼──┐    ┌──────▼──────────┐
                    │   ACCEPTED   │    │     PENDING      │
                    └──────────────┘    └──┬──────┬─────┬──┘
                                          │      │     │
                              ┌───────────▼┐  ┌──▼───┐ │
                              │  ACCEPTED   │  │REJECT│ │
                              │(by organizer)│ │  ED  │ │
                              └─────────────┘  └──────┘ │
                                                        │
                                              ┌─────────▼──┐
                                              │  WITHDRAWN  │
                                              │  (deleted)  │
                                              └─────────────┘
```

Withdrawal is a hard delete (the application record is removed), not a status transition.

## Relationships

```
Application N ──> 1 Participant
Application N ──> 1 Competition
```

- Each application belongs to exactly one participant and one competition.
- One participant can have multiple applications (one per competition).
- One competition can have multiple applications from different participants.
- Applications are deleted when their competition is deleted (cascade).
