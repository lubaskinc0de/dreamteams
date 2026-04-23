from typing import Any

import aiobotocore  # noqa: F401
import botocore  # noqa: F401
import python_multipart  # noqa: F401
import structlog
from opentelemetry import trace as otel_trace


def _inject_otel_context(_logger: object, _method: str, event_dict: dict[str, Any]) -> dict[str, Any]:
    span = otel_trace.get_current_span()
    ctx = span.get_span_context()
    if ctx.is_valid:
        event_dict["trace_id"] = format(ctx.trace_id, "032x")
        event_dict["span_id"] = format(ctx.span_id, "016x")
    return event_dict


def configure_structlog() -> dict[str, Any]:
    """Configure structlog and return log_config."""
    processors = [
        _inject_otel_context,
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.format_exc_info,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
    ]

    structlog.configure(
        processors=[*processors, structlog.stdlib.ProcessorFormatter.wrap_for_formatter],  # type:ignore[list-item]
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    json_formatter = {
        "()": structlog.stdlib.ProcessorFormatter,
        "processor": structlog.processors.JSONRenderer(
            sort_keys=True,
            ensure_ascii=False,
        ),
        "foreign_pre_chain": processors,
    }

    log_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": json_formatter,
        },
        "handlers": {
            "json": {
                "class": "logging.StreamHandler",
                "formatter": "json",
                "stream": "ext://sys.stdout",
            },
        },
        "root": {
            "level": "DEBUG",
            "handlers": ["json"],
        },
        "loggers": {
            "uvicorn": {
                "level": "INFO",
                "handlers": ["json"],
                "propagate": False,
            },
            "uvicorn.error": {
                "level": "CRITICAL",
                "handlers": ["json"],
                "propagate": False,
            },
            "uvicorn.access": {
                "level": "INFO",
                "handlers": ["json"],
                "propagate": False,
            },
            "botocore": {
                "level": "CRITICAL",
                "handlers": ["json"],
                "propagate": False,
            },
            "aiobotocore": {
                "level": "CRITICAL",
                "handlers": ["json"],
                "propagate": False,
            },
            "python_multipart": {
                "level": "CRITICAL",
                "handlers": ["json"],
                "propagate": False,
            },
        },
    }

    return log_config
