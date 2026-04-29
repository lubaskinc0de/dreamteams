from dishka import BaseScope, Provider, Scope, provide_all

from dreamteams_exporter.application.export_applications_sheets.create_job import CreateExportApplicationsJob
from dreamteams_exporter.application.export_applications_sheets.process_job import ExportApplicationsToSheets
from dreamteams_exporter.application.export_applications_sheets.read_job import ReadExportApplicationsJob


class InteractorProvider(Provider):
    """Exposes every exporter interactor at REQUEST scope."""

    scope: BaseScope | None = Scope.REQUEST

    interactors = provide_all(
        CreateExportApplicationsJob,
        ExportApplicationsToSheets,
        ReadExportApplicationsJob,
    )
