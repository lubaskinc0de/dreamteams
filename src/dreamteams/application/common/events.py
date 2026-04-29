from abc import ABC
from dataclasses import dataclass

from dreamteams.entities.common.identifiers import (
    ApplicationFormId,
    ApplicationId,
    CompetitionId,
    CompetitionTagId,
    UserId,
)
from dreamteams.entities.user import BanStatus


class DomainEvent(ABC):  # noqa: B024
    """Base class for events published by application use cases."""


@dataclass(frozen=True, slots=True)
class UserRegistered(DomainEvent):
    """Event emitted when a user registers for an application role."""

    role: str


@dataclass(frozen=True, slots=True)
class UserBlocked(DomainEvent):
    """Event emitted when an admin blocks a user."""

    user_id: UserId
    ban_status: BanStatus


@dataclass(frozen=True, slots=True)
class UserUnblocked(DomainEvent):
    """Event emitted when an admin unblocks a user."""

    user_id: UserId


@dataclass(frozen=True, slots=True)
class CompetitionCreated(DomainEvent):
    """Event emitted when a competition is created."""

    competition_id: CompetitionId


@dataclass(frozen=True, slots=True)
class CompetitionChanged(DomainEvent):
    """Event emitted when a competition changes."""

    competition_id: CompetitionId


@dataclass(frozen=True, slots=True)
class CompetitionDeleted(DomainEvent):
    """Event emitted when a competition is deleted."""

    competition_id: CompetitionId


@dataclass(frozen=True, slots=True)
class CompetitionTagCreated(DomainEvent):
    """Event emitted when a competition tag is created."""

    tag_id: CompetitionTagId


@dataclass(frozen=True, slots=True)
class CompetitionTagDeleted(DomainEvent):
    """Event emitted when a competition tag is deleted."""

    tag_id: CompetitionTagId


@dataclass(frozen=True, slots=True)
class ApplicationFormCreated(DomainEvent):
    """Event emitted when an application form is created."""

    application_form_id: ApplicationFormId
    competition_id: CompetitionId


@dataclass(frozen=True, slots=True)
class ApplicationFormDeleted(DomainEvent):
    """Event emitted when an application form is deleted."""

    application_form_id: ApplicationFormId
    competition_id: CompetitionId


@dataclass(frozen=True, slots=True)
class ApplicationSubmitted(DomainEvent):
    """Event emitted when a participant submits an application."""

    application_id: ApplicationId
    competition_id: CompetitionId


@dataclass(frozen=True, slots=True)
class ApplicationAccepted(DomainEvent):
    """Event emitted when an application is accepted."""

    application_id: ApplicationId
    competition_id: CompetitionId


@dataclass(frozen=True, slots=True)
class ApplicationRejected(DomainEvent):
    """Event emitted when an application is rejected."""

    application_id: ApplicationId
    competition_id: CompetitionId


@dataclass(frozen=True, slots=True)
class ApplicationWithdrawn(DomainEvent):
    """Event emitted when an application is withdrawn."""

    application_id: ApplicationId
    competition_id: CompetitionId


@dataclass(frozen=True, slots=True)
class AvatarAttached(DomainEvent):
    """Event emitted when a user attaches an avatar."""

    user_id: UserId


@dataclass(frozen=True, slots=True)
class AvatarDetached(DomainEvent):
    """Event emitted when a user detaches an avatar."""

    user_id: UserId
