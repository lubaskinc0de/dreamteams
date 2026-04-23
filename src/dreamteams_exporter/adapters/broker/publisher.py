from typing import override

from faststream.nats import NatsBroker

from dreamteams_exporter.adapters.broker.config import NatsConfig
from dreamteams_exporter.adapters.http.config import DreamteamsApiConfig
from dreamteams_exporter.application.common.event_bus import JobEventBus
from dreamteams_exporter.entities.common.identifiers import ExportJobId


class NatsJobEventBus(JobEventBus):
    """Publishes follow-up job events onto NATS JetStream."""

    def __init__(
        self,
        broker: NatsBroker,
        nats_config: NatsConfig,
        api_config: DreamteamsApiConfig,
        auth_token: str,
    ) -> None:
        self._broker = broker
        self._nats_config = nats_config
        self._auth_header_name = api_config.auth_header_name
        self._auth_token = auth_token

    @override
    async def publish_process(self, job_id: ExportJobId) -> None:
        """Publishes ``exporter.jobs.process`` carrying the job id and the forwarded auth header."""
        await self._broker.publish(
            {"job_id": str(job_id)},
            subject=self._nats_config.process_subject,
            stream=self._nats_config.stream_name,
            headers={self._auth_header_name: self._auth_token},
        )
