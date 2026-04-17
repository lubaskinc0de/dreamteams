from abc import abstractmethod
from typing import Protocol


class MetricsGateway(Protocol):
    """Protocol for recording key business metrics."""

    @abstractmethod
    def record_registration(self, *, role: str) -> None:
        """Record a user registration event."""

    @abstractmethod
    def record_competition_created(self) -> None:
        """Record a competition creation event."""

    @abstractmethod
    def record_application_submitted(self) -> None:
        """Record an application submission event."""

    @abstractmethod
    def record_application_accepted(self) -> None:
        """Record an application acceptance event."""

    @abstractmethod
    def record_application_rejected(self) -> None:
        """Record an application rejection event."""

    @abstractmethod
    def record_application_withdrawn(self) -> None:
        """Record an application withdrawal event."""

    @abstractmethod
    def record_application_form_created(self) -> None:
        """Record an application form creation event."""

    @abstractmethod
    def record_application_form_deleted(self) -> None:
        """Record an application form deletion event."""

    @abstractmethod
    def record_avatar_attached(self) -> None:
        """Record an avatar attachment event."""

    @abstractmethod
    def record_avatar_detached(self) -> None:
        """Record an avatar detachment event."""
