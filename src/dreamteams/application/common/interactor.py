import functools
import re
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any, dataclass_transform

from opentelemetry import trace

_tracer = trace.get_tracer("dreamteams.interactors")
_CAMEL_TO_SNAKE = re.compile(r"(?<!^)(?=[A-Z])")


def _span_name(class_name: str) -> str:
    return f"interactor.{_CAMEL_TO_SNAKE.sub('_', class_name).lower()}"


def _wrap_execute[**P, R](execute: Callable[P, Awaitable[R]], span_name: str) -> Callable[P, Awaitable[R]]:
    @functools.wraps(execute)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        with _tracer.start_as_current_span(span_name):
            return await execute(*args, **kwargs)

    return wrapper


@dataclass_transform(kw_only_default=True, frozen_default=True)
def interactor[ClsT](cls: type[ClsT]) -> type[ClsT]:
    """Decorator that transforms a class into a frozen dataclass and wraps ``execute`` in an OTel span."""
    execute: Any = getattr(cls, "execute", None)
    if execute is not None:
        cls.execute = _wrap_execute(execute, _span_name(cls.__name__))  # type: ignore[attr-defined]
    return dataclass(slots=True, kw_only=True, frozen=True)(cls)
