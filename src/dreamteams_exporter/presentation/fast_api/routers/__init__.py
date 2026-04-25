from fastapi import FastAPI

from dreamteams_exporter.presentation.fast_api.routers.exports import router as exports_router
from dreamteams_exporter.presentation.fast_api.routers.root import router as root_router


def include_routers(app: FastAPI) -> None:
    """Attach every presentation-level router to the given FastAPI app."""
    app.include_router(root_router)
    app.include_router(exports_router)


__all__ = ["include_routers"]
