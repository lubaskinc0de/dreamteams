from abc import abstractmethod
from dataclasses import dataclass
from typing import Any, ClassVar, Protocol, override
from uuid import uuid4

from fastapi.requests import Request

from dreamteams.entities.errors.base import AppError, app_error

type TraceId = str


@app_error
class MissingTraceIdError(AppError):
    """Error that is raised when trace id is required but cannot be extracted from request."""

    header: str
    message: str = "Missing trace id"
    code: ClassVar[str] = "MISSING_TRACE_ID"

    @property
    @override
    def meta(self) -> dict[str, Any]:
        return {
            "header": self.header,
        }


@dataclass(slots=True, frozen=True, kw_only=True)
class TracingConfig:
    """Tracing configuration."""

    trace_id_header: str
    trace_id_required: bool = False


class TraceProvider(Protocol):
    """``TraceId`` provider."""

    @abstractmethod
    def get_trace_id(self) -> TraceId:
        """Provide ``TraceId``."""


class HTTPTraceProvider(TraceProvider):
    """Provide ``TraceId`` from HTTP request headers."""

    _request: Request
    _config: TracingConfig

    def __init__(self, request: Request, config: TracingConfig) -> None:
        self._request = request
        self._config = config

    @override
    def get_trace_id(self) -> TraceId:
        trace_id = self._request.headers.get(self._config.trace_id_header)
        if trace_id is None and self._config.trace_id_required:
            raise MissingTraceIdError(header=self._config.trace_id_header)

        if trace_id is None:
            trace_id = uuid4().hex

        return trace_id
