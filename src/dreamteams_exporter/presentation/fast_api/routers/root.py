import structlog
from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from faststream.nats import NatsBroker
from redis.asyncio import Redis

from dreamteams_common.logger import Logger

logger: Logger = structlog.get_logger(__name__)
router = APIRouter(tags=["Root"], route_class=DishkaRoute)


@router.get("/internal/alive")
async def alive() -> JSONResponse:
    """HTTP endpoint for liveness probe."""
    return JSONResponse(status_code=200, content={})


@router.get("/internal/ready")
async def ready(
    redis: FromDishka[Redis],
    broker: FromDishka[NatsBroker],
) -> JSONResponse:
    """HTTP endpoint for readiness probe."""
    try:
        if not await redis.ping():  # type: ignore[misc]
            return JSONResponse(status_code=503, content={})
        if not broker.connection.is_connected:
            return JSONResponse(status_code=503, content={})
    except Exception as exc:  # noqa: BLE001
        await logger.awarning("Exporter dependency is not ready", exc_info=exc)
        return JSONResponse(status_code=503, content={})

    return JSONResponse(status_code=200, content={})
