from collections.abc import AsyncIterator

import pytest
from asgi_lifespan import LifespanManager
from faststream.nats import NatsBroker, TestNatsBroker
from faststream.nats.publisher.usecase import LogicPublisher

from dreamteams_exporter.bootstrap.config.loader import Config as ExporterConfig
from tests.integration.api_client import ApiClient
from tests.integration.exporter.container import create_exporter_test_app, setup_exporter_test_worker


@pytest.fixture
async def exporter_app(
    exporter_config: ExporterConfig,
    api_client: ApiClient,
    exporter_broker: NatsBroker,
    process_job_publisher: LogicPublisher,
) -> AsyncIterator[object]:
    """Exporter HTTP app with worker handlers registered before TestNatsBroker starts."""
    setup_exporter_test_worker(exporter_config, api_client, exporter_broker)
    app = create_exporter_test_app(exporter_config, api_client, exporter_broker, process_job_publisher)
    async with TestNatsBroker(exporter_broker, connect_only=False), LifespanManager(app):
        yield app
