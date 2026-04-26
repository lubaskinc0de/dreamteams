from dataclasses import dataclass

from dreamteams_exporter.entities.common.identifiers import ApplicationFormId


@dataclass(slots=True, kw_only=True)
class ApplicationFormField:
    """Application form field data needed by the exporter."""

    name: str


@dataclass(slots=True, kw_only=True)
class ApplicationForm:
    """Application form projection needed by the exporter."""

    id: ApplicationFormId
    fields: list[ApplicationFormField]
