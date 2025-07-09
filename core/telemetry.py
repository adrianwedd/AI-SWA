"""OpenTelemetry setup utilities for AI-SWA."""

from __future__ import annotations

import logging
from typing import Tuple

try:
    from opentelemetry import metrics, trace
    from opentelemetry.metrics import set_meter_provider, get_meter_provider
    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
    from opentelemetry.exporter.prometheus import PrometheusMetricReader, start_http_server
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
    from opentelemetry.sdk._logs.export import BatchLogRecordProcessor, ConsoleLogExporter
except Exception:  # pragma: no cover - optional dependency
    metrics = trace = None


def setup_telemetry(service_name: str = "ai_swa", metrics_port: int = 8000) -> Tuple[object, object]:
    """Configure OpenTelemetry providers and start the Prometheus metrics server."""

    if metrics is None:
        raise ImportError("opentelemetry is required for telemetry")

    resource = Resource.create({"service.name": service_name})

    # Metrics provider with Prometheus exporter
    reader = PrometheusMetricReader()
    meter_provider = MeterProvider(metric_readers=[reader], resource=resource)
    set_meter_provider(meter_provider)
    server, thread = start_http_server(port=metrics_port)

    # Tracing provider with console exporter
    tracer_provider = TracerProvider(resource=resource)
    tracer_provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
    trace.set_tracer_provider(tracer_provider)

    # Logging provider with console exporter
    logger_provider = LoggerProvider(resource=resource)
    logger_provider.add_log_record_processor(BatchLogRecordProcessor(ConsoleLogExporter()))
    handler = LoggingHandler(level=logging.INFO, logger_provider=logger_provider)
    logging.getLogger().addHandler(handler)

    return server, thread
