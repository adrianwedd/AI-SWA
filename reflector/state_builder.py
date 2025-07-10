from __future__ import annotations

from typing import Dict

from core.observability import MetricsProvider


class StateBuilder:
    """Generate a state vector from observability metrics."""

    def __init__(self, metrics_provider: MetricsProvider) -> None:
        self.metrics_provider = metrics_provider

    def build(self) -> Dict[str, float]:
        """Return numeric metrics of interest with defaults."""
        metrics = self.metrics_provider.collect()
        cpu = float(metrics.get("cpu", 0))
        memory = float(metrics.get("memory", 0))
        error_rate = float(metrics.get("error_rate", 0))
        state = {
            "cpu": cpu,
            "memory": memory,
            "error_rate": error_rate,
        }
        return state

    def vector(self) -> list[float]:
        """Return ``build()`` values sorted by key for stable ordering."""
        state = self.build()
        return [state[k] for k in sorted(state.keys())]
