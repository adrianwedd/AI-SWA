from __future__ import annotations

from typing import Dict

from core.observability import MetricsProvider


class StateBuilder:
    """Generate a numerical state representation from observability data."""

    def __init__(self, metrics_provider: MetricsProvider) -> None:
        self.metrics_provider = metrics_provider

    def build(self) -> Dict[str, float]:
        metrics = self.metrics_provider.collect()
        return {
            k: float(v)
            for k, v in metrics.items()
            if isinstance(v, (int, float))
        }
