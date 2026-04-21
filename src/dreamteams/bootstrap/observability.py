import os
from dataclasses import dataclass
from uuid import uuid4

from opentelemetry import metrics, trace
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import SERVICE_INSTANCE_ID, SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.trace.sampling import ParentBased, TraceIdRatioBased


@dataclass(slots=True, frozen=True, kw_only=True)
class OTelConfig:
    """OpenTelemetry configuration."""

    endpoint: str
    service_name: str
    sample_ratio: float = 0.1
    metric_export_interval_ms: int = 10000
    instrument_sqlalchemy: bool = False
    enabled: bool = True


def setup_observability(config: OTelConfig) -> None:
    """Initialize global TracerProvider and MeterProvider — both push to the OTel Collector via OTLP."""
    if not config.enabled:
        return

    # Per-process unique id so multi-worker setups produce distinct Prometheus timeseries
    # rather than collapsing into one (last-write-wins).
    resource = Resource.create(
        {
            SERVICE_NAME: config.service_name,
            SERVICE_INSTANCE_ID: f"{config.service_name}-{os.getpid()}-{uuid4().hex[:8]}",
        },
    )

    sampler = ParentBased(root=TraceIdRatioBased(config.sample_ratio))
    tracer_provider = TracerProvider(resource=resource, sampler=sampler)
    tracer_provider.add_span_processor(
        BatchSpanProcessor(OTLPSpanExporter(endpoint=f"{config.endpoint}/v1/traces")),
    )
    trace.set_tracer_provider(tracer_provider)

    metric_reader = PeriodicExportingMetricReader(
        OTLPMetricExporter(endpoint=f"{config.endpoint}/v1/metrics"),
        export_interval_millis=config.metric_export_interval_ms,
    )
    meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
    metrics.set_meter_provider(meter_provider)
