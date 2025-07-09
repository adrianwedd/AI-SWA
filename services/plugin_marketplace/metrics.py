from __future__ import annotations

"""Prometheus metrics for the plugin marketplace service."""

try:
    from opentelemetry import metrics
except Exception:  # pragma: no cover - optional dependency
    metrics = None

if metrics:
    _meter = metrics.get_meter_provider().get_meter(__name__)
    DOWNLOADS = _meter.create_counter(
        "plugin_downloads_total",
        description="Number of plugin downloads",
    )
    ERRORS = _meter.create_counter(
        "plugin_download_errors_total",
        description="Number of failed download attempts",
    )
else:  # pragma: no cover - telemetry optional
    DOWNLOADS = None
    ERRORS = None
