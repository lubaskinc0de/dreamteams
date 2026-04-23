from dataclasses import dataclass


@dataclass(slots=True, frozen=True, kw_only=True)
class OTelConfig:
    """OpenTelemetry configuration."""

    endpoint: str
    service_name: str
    sample_ratio: float = 0.1
    metric_export_interval_ms: int = 10000
    instrument_sqlalchemy: bool = False
    enabled: bool = True
