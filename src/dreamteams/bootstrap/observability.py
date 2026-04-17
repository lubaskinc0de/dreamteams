from dataclasses import dataclass

from opentelemetry import metrics, trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


@dataclass(slots=True, frozen=True, kw_only=True)
class OTelConfig:
    """OpenTelemetry configuration."""

    endpoint: str
    service_name: str


def setup_observability(config: OTelConfig) -> None:
    """Initialize global TracerProvider and MeterProvider."""
    resource = Resource.create({SERVICE_NAME: config.service_name})

    tracer_provider = TracerProvider(resource=resource)
    tracer_provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=config.endpoint)))
    trace.set_tracer_provider(tracer_provider)

    meter_provider = MeterProvider(resource=resource, metric_readers=[PrometheusMetricReader()])
    metrics.set_meter_provider(meter_provider)
