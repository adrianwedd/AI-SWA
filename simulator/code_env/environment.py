from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Any

from core.production_simulator import (
    Service,
    Database,
    LoadBalancer,
    ProductionSimulator,
    SimulationMetricsProvider,
)
from core.observability import MetricsProvider
from core.task import Task


@dataclass
class CodeEnv:
    """Simulation environment mirroring production behavior."""

    workload_path: Path
    metrics_provider: Optional[MetricsProvider] = None

    def __post_init__(self) -> None:
        provider = self.metrics_provider or SimulationMetricsProvider
        if isinstance(provider, type):
            provider = provider(self)  # type: ignore[arg-type]
        self.simulator = ProductionSimulator(
            workload_path=self.workload_path,
            metrics_provider=provider,
        )
        self.tasks: List[Task] = []

    # --------------------------------------------------------------
    def add_service(self, service: Service) -> None:
        self.simulator.add_service(service)

    # --------------------------------------------------------------
    def add_database(self, db: Database) -> None:
        self.simulator.add_database(db)

    # --------------------------------------------------------------
    def add_load_balancer(self, lb: LoadBalancer) -> None:
        self.simulator.add_load_balancer(lb)

    # --------------------------------------------------------------
    def submit_task(self, task: Task) -> None:
        """Queue ``task`` for execution in the environment."""
        self.tasks.append(task)

    # --------------------------------------------------------------
    def next_task(self) -> Optional[Task]:
        """Return the next queued task if available."""
        if self.tasks:
            return self.tasks.pop(0)
        return None

    # --------------------------------------------------------------
    def step(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Advance the simulation one event using ``action``."""
        return self.simulator.step(action)

    # --------------------------------------------------------------
    def collect_metrics(self) -> Dict[str, Any]:
        """Return current environment metrics."""
        return self.simulator.collect_metrics()
