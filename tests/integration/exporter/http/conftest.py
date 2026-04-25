from collections.abc import AsyncIterator

import pytest
from asgi_lifespan import LifespanManager
from faststream.nats import JStream, NatsBroker, TestNatsBroker
from faststream.nats.publisher.usecase import LogicPublisher
from nats.js.api import DeliverPolicy

from dreamteams_exporter.bootstrap.config.loader import Config as ExporterConfig
from tests.integration.api_client import ApiClient
from tests.integration.exporter.container import create_exporter_test_app


@pytest.fixture
async def exporter_app(
    exporter_config: ExporterConfig,
    api_client: ApiClient,
    exporter_broker: NatsBroker,
    process_job_publisher: LogicPublisher,
) -> AsyncIterator[object]:
    """Exporter HTTP app with TestNatsBroker."""

    @exporter_broker.subscriber(
        exporter_config.nats.process_subject,
        stream=JStream(name=exporter_config.nats.stream_name),
        deliver_policy=DeliverPolicy.NEW,
    )
    async def _noop(_: dict[str, object]) -> None:
        pass

    app = create_exporter_test_app(exporter_config, api_client, exporter_broker, process_job_publisher)
    async with TestNatsBroker(exporter_broker, connect_only=False), LifespanManager(app):
        yield app
