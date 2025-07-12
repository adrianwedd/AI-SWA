from __future__ import annotations

"""Helpers for generating feature vectors from observability metrics."""

from pathlib import Path
from typing import List

from core.observability import MetricsProvider


def from_path(metrics_path: Path) -> List[float]:
    """Return a feature vector using metrics from ``metrics_path``."""
    provider = MetricsProvider(metrics_path)
    metrics = provider.collect()
    numeric = {
        k: float(v)
        for k, v in metrics.items()
        if isinstance(v, (int, float))
    }
    return [numeric[k] for k in sorted(numeric.keys())]
