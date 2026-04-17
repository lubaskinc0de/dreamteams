from typing import override

from opentelemetry import metrics

from dreamteams.application.common.metrics import MetricsGateway

_meter = metrics.get_meter("dreamteams.business")


class OTelMetricsGateway(MetricsGateway):
    """OTel-backed implementation of the ``MetricsGateway`` protocol."""

    def __init__(self) -> None:
        self._registrations = _meter.create_counter(
            name="dreamteams.registrations",
            description="User registrations by role",
            unit="1",
        )
        self._competitions_created = _meter.create_counter(
            name="dreamteams.competitions_created",
            description="Competitions created",
            unit="1",
        )
        self._applications_submitted = _meter.create_counter(
            name="dreamteams.applications_submitted",
            description="Competition applications submitted",
            unit="1",
        )
        self._applications_accepted = _meter.create_counter(
            name="dreamteams.applications_accepted",
            description="Competition applications accepted",
            unit="1",
        )
        self._applications_rejected = _meter.create_counter(
            name="dreamteams.applications_rejected",
            description="Competition applications rejected",
            unit="1",
        )
        self._applications_withdrawn = _meter.create_counter(
            name="dreamteams.applications_withdrawn",
            description="Competition applications withdrawn",
            unit="1",
        )
        self._application_forms_created = _meter.create_counter(
            name="dreamteams.application_forms_created",
            description="Application forms created",
            unit="1",
        )
        self._application_forms_deleted = _meter.create_counter(
            name="dreamteams.application_forms_deleted",
            description="Application forms deleted",
            unit="1",
        )
        self._avatars_attached = _meter.create_counter(
            name="dreamteams.avatars_attached",
            description="User avatars attached",
            unit="1",
        )
        self._avatars_detached = _meter.create_counter(
            name="dreamteams.avatars_detached",
            description="User avatars detached",
            unit="1",
        )

    @override
    def record_registration(self, *, role: str) -> None:
        """Increment registration counter for the given role."""
        self._registrations.add(1, {"role": role})

    @override
    def record_competition_created(self) -> None:
        """Increment competition creation counter."""
        self._competitions_created.add(1)

    @override
    def record_application_submitted(self) -> None:
        """Increment application submission counter."""
        self._applications_submitted.add(1)

    @override
    def record_application_accepted(self) -> None:
        """Increment application acceptance counter."""
        self._applications_accepted.add(1)

    @override
    def record_application_rejected(self) -> None:
        """Increment application rejection counter."""
        self._applications_rejected.add(1)

    @override
    def record_application_withdrawn(self) -> None:
        """Increment application withdrawal counter."""
        self._applications_withdrawn.add(1)

    @override
    def record_application_form_created(self) -> None:
        """Increment application form creation counter."""
        self._application_forms_created.add(1)

    @override
    def record_application_form_deleted(self) -> None:
        """Increment application form deletion counter."""
        self._application_forms_deleted.add(1)

    @override
    def record_avatar_attached(self) -> None:
        """Increment avatar attachment counter."""
        self._avatars_attached.add(1)

    @override
    def record_avatar_detached(self) -> None:
        """Increment avatar detachment counter."""
        self._avatars_detached.add(1)
