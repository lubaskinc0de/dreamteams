from collections.abc import Awaitable, Callable

import structlog
from fastapi import Request, Response
from opentelemetry import trace

_tracer = trace.get_tracer(__name__)


async def tracing_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    """Bind OTel trace_id and span_id into structlog context for each request."""
    span = trace.get_current_span()
    ctx = span.get_span_context()
    context = {}
    if ctx.is_valid:
        context = {
            "trace_id": format(ctx.trace_id, "032x"),
            "span_id": format(ctx.span_id, "016x"),
        }

    with structlog.contextvars.bound_contextvars(**context):
        response = await call_next(request)

        with _tracer.start_as_current_span("fastapi.middleware.after_call") as after_call:
            after_call.set_attribute("http.status_code", response.status_code)
            return response
