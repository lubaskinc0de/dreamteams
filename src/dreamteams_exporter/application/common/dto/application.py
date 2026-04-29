from dataclasses import dataclass

from dreamteams_exporter.entities.application.entity import Application


@dataclass(slots=True, kw_only=True, frozen=True)
class ApplicationsPage:
    """One page of applications."""

    items: list[Application]
    page: int
    page_size: int
    total: int

    @property
    def has_next(self) -> bool:
        """True when there are more pages left to fetch."""
        return self.page * self.page_size < self.total
