from dishka import Provider, Scope, WithParents, provide

from dreamteams.adapters.metrics import OTelMetricsGateway


class MetricsProvider(Provider):
    """Dishka provider that registers the OTel metrics gateway."""

    metrics_gateway = provide(WithParents[OTelMetricsGateway], scope=Scope.APP)
