from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import aiohttp

from dreamteams_exporter.adapters.http.config import DreamteamsApiConfig


@asynccontextmanager
async def aiohttp_session(config: DreamteamsApiConfig) -> AsyncIterator[aiohttp.ClientSession]:
    """App-scoped ``aiohttp.ClientSession`` configured with shared timeouts."""
    timeout = aiohttp.ClientTimeout(
        total=config.timeout_seconds,
        connect=config.connect_timeout_seconds,
        sock_connect=config.sock_connect_timeout_seconds,
        sock_read=config.sock_read_timeout_seconds,
    )
    async with aiohttp.ClientSession(timeout=timeout) as session:
        yield session
