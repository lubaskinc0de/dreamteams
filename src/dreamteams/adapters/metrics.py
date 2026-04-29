from opentelemetry import metrics

from dreamteams.application.common.events import (
    ApplicationAccepted,
    ApplicationFormCreated,
    ApplicationFormDeleted,
    ApplicationRejected,
    ApplicationSubmitted,
    ApplicationWithdrawn,
    AvatarAttached,
    AvatarDetached,
    CompetitionCreated,
    DomainEvent,
    UserRegistered,
)

_meter = metrics.get_meter("dreamteams.business")


class RegistrationMetricsEventHandler:
    """Records user registration metrics."""

    def __init__(self) -> None:
        self._registrations = _meter.create_counter(
            name="dreamteams.registrations",
            description="User registrations by role",
            unit="1",
        )

    async def __call__(self, event: DomainEvent) -> None:
        """Increment registration counter for the received event."""
        if not isinstance(event, UserRegistered):
            msg = f"{type(self).__name__} received invalid event: {type(event).__name__}"
            raise TypeError(msg)
        self._registrations.add(1, {"role": event.role})


class CompetitionCreatedMetricsEventHandler:
    """Records competition creation metrics."""

    def __init__(self) -> None:
        self._counter = _meter.create_counter(
            name="dreamteams.competitions_created",
            description="Competitions created",
            unit="1",
        )

    async def __call__(self, event: DomainEvent) -> None:
        """Increment competition creation counter for the received event."""
        if not isinstance(event, CompetitionCreated):
            msg = f"{type(self).__name__} received invalid event: {type(event).__name__}"
            raise TypeError(msg)
        self._counter.add(1)


class ApplicationSubmittedMetricsEventHandler:
    """Records application submission metrics."""

    def __init__(self) -> None:
        self._counter = _meter.create_counter(
            name="dreamteams.applications_submitted",
            description="Competition applications submitted",
            unit="1",
        )

    async def __call__(self, event: DomainEvent) -> None:
        """Increment application submission counter for the received event."""
        if not isinstance(event, ApplicationSubmitted):
            msg = f"{type(self).__name__} received invalid event: {type(event).__name__}"
            raise TypeError(msg)
        self._counter.add(1)


class ApplicationAcceptedMetricsEventHandler:
    """Records application acceptance metrics."""

    def __init__(self) -> None:
        self._counter = _meter.create_counter(
            name="dreamteams.applications_accepted",
            description="Competition applications accepted",
            unit="1",
        )

    async def __call__(self, event: DomainEvent) -> None:
        """Increment application acceptance counter for the received event."""
        if not isinstance(event, ApplicationAccepted):
            msg = f"{type(self).__name__} received invalid event: {type(event).__name__}"
            raise TypeError(msg)
        self._counter.add(1)


class ApplicationRejectedMetricsEventHandler:
    """Records application rejection metrics."""

    def __init__(self) -> None:
        self._counter = _meter.create_counter(
            name="dreamteams.applications_rejected",
            description="Competition applications rejected",
            unit="1",
        )

    async def __call__(self, event: DomainEvent) -> None:
        """Increment application rejection counter for the received event."""
        if not isinstance(event, ApplicationRejected):
            msg = f"{type(self).__name__} received invalid event: {type(event).__name__}"
            raise TypeError(msg)
        self._counter.add(1)


class ApplicationWithdrawnMetricsEventHandler:
    """Records application withdrawal metrics."""

    def __init__(self) -> None:
        self._counter = _meter.create_counter(
            name="dreamteams.applications_withdrawn",
            description="Competition applications withdrawn",
            unit="1",
        )

    async def __call__(self, event: DomainEvent) -> None:
        """Increment application withdrawal counter for the received event."""
        if not isinstance(event, ApplicationWithdrawn):
            msg = f"{type(self).__name__} received invalid event: {type(event).__name__}"
            raise TypeError(msg)
        self._counter.add(1)


class ApplicationFormCreatedMetricsEventHandler:
    """Records application form creation metrics."""

    def __init__(self) -> None:
        self._counter = _meter.create_counter(
            name="dreamteams.application_forms_created",
            description="Application forms created",
            unit="1",
        )

    async def __call__(self, event: DomainEvent) -> None:
        """Increment application form creation counter for the received event."""
        if not isinstance(event, ApplicationFormCreated):
            msg = f"{type(self).__name__} received invalid event: {type(event).__name__}"
            raise TypeError(msg)
        self._counter.add(1)


class ApplicationFormDeletedMetricsEventHandler:
    """Records application form deletion metrics."""

    def __init__(self) -> None:
        self._counter = _meter.create_counter(
            name="dreamteams.application_forms_deleted",
            description="Application forms deleted",
            unit="1",
        )

    async def __call__(self, event: DomainEvent) -> None:
        """Increment application form deletion counter for the received event."""
        if not isinstance(event, ApplicationFormDeleted):
            msg = f"{type(self).__name__} received invalid event: {type(event).__name__}"
            raise TypeError(msg)
        self._counter.add(1)


class AvatarAttachedMetricsEventHandler:
    """Records avatar attachment metrics."""

    def __init__(self) -> None:
        self._counter = _meter.create_counter(
            name="dreamteams.avatars_attached",
            description="User avatars attached",
            unit="1",
        )

    async def __call__(self, event: DomainEvent) -> None:
        """Increment avatar attachment counter for the received event."""
        if not isinstance(event, AvatarAttached):
            msg = f"{type(self).__name__} received invalid event: {type(event).__name__}"
            raise TypeError(msg)
        self._counter.add(1)


class AvatarDetachedMetricsEventHandler:
    """Records avatar detachment metrics."""

    def __init__(self) -> None:
        self._counter = _meter.create_counter(
            name="dreamteams.avatars_detached",
            description="User avatars detached",
            unit="1",
        )

    async def __call__(self, event: DomainEvent) -> None:
        """Increment avatar detachment counter for the received event."""
        if not isinstance(event, AvatarDetached):
            msg = f"{type(self).__name__} received invalid event: {type(event).__name__}"
            raise TypeError(msg)
        self._counter.add(1)
