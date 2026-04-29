from typing import Any

from opentelemetry import metrics
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncEngine

_meter = metrics.get_meter("dreamteams.db")


def register_pool_metrics(engine: AsyncEngine) -> None:
    """Wire SQLAlchemy pool events to OTel counters so saturation and connect churn are observable."""
    checked_out = _meter.create_up_down_counter(
        name="dreamteams.db.pool.checked_out",
        description="Connections currently checked out from the pool",
    )
    new_connections = _meter.create_counter(
        name="dreamteams.db.pool.new_connections",
        description="New physical database connections established",
    )
    invalidated = _meter.create_counter(
        name="dreamteams.db.pool.invalidated",
        description="Connections invalidated and dropped from the pool",
    )

    sync_engine = engine.sync_engine

    @event.listens_for(sync_engine, "connect")
    def _on_connect(_dbapi_conn: Any, _record: Any) -> None:
        new_connections.add(1)

    @event.listens_for(sync_engine, "checkout")
    def _on_checkout(_dbapi_conn: Any, _record: Any, _proxy: Any) -> None:
        checked_out.add(1)

    @event.listens_for(sync_engine, "checkin")
    def _on_checkin(_dbapi_conn: Any, _record: Any) -> None:
        checked_out.add(-1)

    @event.listens_for(sync_engine, "invalidate")
    def _on_invalidate(_dbapi_conn: Any, _record: Any, _exception: Any) -> None:
        invalidated.add(1)
