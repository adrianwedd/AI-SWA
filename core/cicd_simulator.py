from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import random

from .observability import MetricsProvider
from .production_simulator import SimulationMetricsProvider


@dataclass
class BuildJob:
    """A CI/CD job with a risk of failure."""

    risk: float = 0.1


class CICDSimulator:
    """Minimal CI/CD pipeline simulator."""

    def __init__(
        self,
        metrics_provider: Optional[MetricsProvider] = None,
        seed: Optional[int] = None,
    ) -> None:
        self.metrics_provider = metrics_provider
        self.random = random.Random(seed)
        self.queue: List[BuildJob] = []
        self._metrics: Dict[str, Any] = {
            "queued_jobs": 0,
            "successful_builds": 0,
            "failed_builds": 0,
        }
        self._seed = seed

    # --------------------------------------------------------------
    def reset(self) -> None:
        self.random = random.Random(self._seed)
        self.queue.clear()
        self._metrics = {
            "queued_jobs": 0,
            "successful_builds": 0,
            "failed_builds": 0,
        }

    # --------------------------------------------------------------
    def add_job(self, job: Optional[BuildJob] = None) -> None:
        self.queue.append(job or BuildJob())
        self._metrics["queued_jobs"] = len(self.queue)

    # --------------------------------------------------------------
    def step(self, action: Dict[str, Any]) -> Dict[str, Any]:
        agents = action.get("agents", 1)
        for _ in range(min(agents, len(self.queue))):
            job = self.queue.pop(0)
            if self.random.random() < job.risk:
                self._metrics["failed_builds"] += 1
            else:
                self._metrics["successful_builds"] += 1
        self._metrics["queued_jobs"] = len(self.queue)
        metrics = self.collect_metrics()
        if self.metrics_provider and not isinstance(self.metrics_provider, SimulationMetricsProvider):
            metrics.update(self.metrics_provider.collect())
        return {"metrics": metrics}

    # --------------------------------------------------------------
    def collect_metrics(self) -> Dict[str, Any]:
        return dict(self._metrics)
