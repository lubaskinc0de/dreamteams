from collections.abc import Awaitable, Callable

import structlog
from fastapi import Request, Response
from opentelemetry import trace


async def tracing_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    """Bind OTel trace_id and span_id into structlog context for each request."""
    span = trace.get_current_span()
    ctx = span.get_span_context()
    if ctx.is_valid:
        with structlog.contextvars.bound_contextvars(
            trace_id=format(ctx.trace_id, "032x"),
            span_id=format(ctx.span_id, "016x"),
        ):
            return await call_next(request)
    return await call_next(request)
