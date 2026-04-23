from abc import abstractmethod
from collections.abc import Iterable
from typing import Protocol

from dreamteams_exporter.entities.application.entity import Application


class SpreadsheetSession(Protocol):
    """Open session into which the interactor pushes batches of rows one at a time."""

    @abstractmethod
    async def write_rows(self, rows: Iterable[Application]) -> None:
        """Appends a batch of rows to the spreadsheet."""
        raise NotImplementedError

    @abstractmethod
    async def finish(self) -> str:
        """Finalises the spreadsheet and returns the URL of the stored file."""
        raise NotImplementedError

    @abstractmethod
    async def abort(self) -> None:
        """Cancels the session and releases any partial state."""
        raise NotImplementedError


class SpreadsheetExporter(Protocol):
    """Starts a new spreadsheet-export session keyed by a stable identifier."""

    @abstractmethod
    async def start(self, *, key: str) -> SpreadsheetSession:
        """Opens a session to which rows can be streamed in batches."""
        raise NotImplementedError
