"""Prometheus metrics for marketplace analytics."""

from __future__ import annotations

try:
    from prometheus_client import Counter
except Exception:  # pragma: no cover - optional dependency
    Counter = None  # type: ignore

if Counter:
    DOWNLOADS = Counter(
        "plugin_downloads_total",
        "Number of plugin downloads",
    )
    RATINGS = Counter(
        "plugin_ratings_total",
        "Number of rating submissions",
    )
    SEARCH_QUERIES = Counter(
        "plugin_search_queries_total",
        "Number of plugin search queries",
    )
else:  # pragma: no cover - metrics optional
    DOWNLOADS = RATINGS = SEARCH_QUERIES = None
