"""OpenTelemetry setup utilities for SelfArchitectAI."""

from __future__ import annotations

import logging
import os
from typing import Tuple

try:
    from opentelemetry import metrics, trace
    from opentelemetry.metrics import set_meter_provider, get_meter_provider
    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
    from opentelemetry.exporter.prometheus import PrometheusMetricReader, start_http_server
    # OTLP exporter is optional and may require extra dependencies
    try:
        from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
    except Exception:  # pragma: no cover - optional dependency
        OTLPMetricExporter = None
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
    from opentelemetry.sdk._logs.export import BatchLogRecordProcessor, ConsoleLogExporter
except Exception:  # pragma: no cover - optional dependency
    metrics = trace = None


def setup_telemetry(
    service_name: str = "ai_swa",
    metrics_port: int = 8000,
    otlp_endpoint: str | None = None,
    otlp_cert_path: str | None = None,
    jaeger_endpoint: str | None = None,
) -> Tuple[object, object]:
    """Configure OpenTelemetry providers and start the Prometheus metrics server.

    If ``otlp_endpoint`` is provided (or ``OTEL_EXPORTER_OTLP_ENDPOINT`` is set in
    the environment), metrics are also exported via OTLP to that endpoint. When a
    certificate path is supplied, it is used to secure the connection.
    """

    if metrics is None:
        raise ImportError("opentelemetry is required for telemetry")

    resource = Resource.create({"service.name": service_name})

    metric_readers = []

    # Export metrics via OTLP if configured
    otlp_endpoint = otlp_endpoint or os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
    otlp_cert_path = otlp_cert_path or os.getenv("OTEL_EXPORTER_OTLP_CERTIFICATE")
    if otlp_endpoint and OTLPMetricExporter:
        exporter = OTLPMetricExporter(
            endpoint=otlp_endpoint,
            insecure=not bool(otlp_cert_path),
            certificate_file=otlp_cert_path,
        )
        metric_readers.append(PeriodicExportingMetricReader(exporter))

    # Metrics provider with Prometheus exporter for scraping
    prom_reader = PrometheusMetricReader()
    metric_readers.append(prom_reader)

    meter_provider = MeterProvider(metric_readers=metric_readers, resource=resource)
    set_meter_provider(meter_provider)
    server, thread = start_http_server(port=metrics_port)

    # Tracing provider with optional Jaeger or OTLP exporter
    tracer_provider = TracerProvider(resource=resource)
    jaeger_endpoint = jaeger_endpoint or os.getenv("JAEGER_ENDPOINT")
    if jaeger_endpoint:
        try:
            from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
            exporter = OTLPSpanExporter(endpoint=jaeger_endpoint, insecure=True)
            tracer_provider.add_span_processor(BatchSpanProcessor(exporter))
        except Exception:  # pragma: no cover - optional
            pass
    elif otlp_endpoint:
        try:
            from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
            exporter = OTLPSpanExporter(
                endpoint=otlp_endpoint,
                insecure=not bool(otlp_cert_path),
                certificate_file=otlp_cert_path,
            )
            tracer_provider.add_span_processor(BatchSpanProcessor(exporter))
        except Exception:  # pragma: no cover - optional
            pass
    tracer_provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
    trace.set_tracer_provider(tracer_provider)

    # Logging provider with console exporter
    logger_provider = LoggerProvider(resource=resource)
    logger_provider.add_log_record_processor(BatchLogRecordProcessor(ConsoleLogExporter()))
    handler = LoggingHandler(level=logging.INFO, logger_provider=logger_provider)
    logging.getLogger().addHandler(handler)

    return server, thread
