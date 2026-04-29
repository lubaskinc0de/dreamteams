from abc import abstractmethod
from collections.abc import Iterable
from typing import Protocol

from dreamteams_exporter.application.common.dto.export_row import ExportRow


class SpreadsheetSession(Protocol):
    """Open session into which the interactor pushes batches of rows one at a time."""

    @abstractmethod
    async def write_rows(self, rows: Iterable[ExportRow]) -> None:
        """Appends a batch of cell rows to the spreadsheet."""
        raise NotImplementedError

    @abstractmethod
    async def finish(self) -> str:
        """Finalises the spreadsheet and returns the private storage key of the stored file."""
        raise NotImplementedError

    @abstractmethod
    async def abort(self) -> None:
        """Cancels the session and releases any partial state."""
        raise NotImplementedError


class SpreadsheetExporter(Protocol):
    """Starts a new spreadsheet-export session keyed by a stable identifier."""

    @abstractmethod
    async def start(self, *, key: str, headers: list[str]) -> SpreadsheetSession:
        """Opens a session whose first line is ``headers``; subsequent batches stream into it."""
        raise NotImplementedError

    @abstractmethod
    async def get_download_url(self, key: str) -> str:
        """Return a short-lived signed URL for a private stored spreadsheet key."""
        raise NotImplementedError
