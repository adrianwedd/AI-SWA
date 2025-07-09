from __future__ import annotations

"""Simplified simulation of the production environment for RL training."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Any
import json
import random

from .observability import MetricsProvider


@dataclass
class Service:
    """Represents a core service in the production environment."""

    name: str
    capacity: int
    latency_ms: int = 0


@dataclass
class Database:
    """Represents a backing database."""

    name: str
    max_connections: int
    active_connections: int = 0


@dataclass
class LoadBalancer:
    """Simple load balancer distributing requests across services."""

    name: str
    targets: List[Service] = field(default_factory=list)


class ProductionSimulator:
    """High-level simulator mirroring production behavior."""

    def __init__(self, workload_path: Path, metrics_provider: Optional[MetricsProvider] = None) -> None:
        self.workload_path = Path(workload_path)
        self.metrics_provider = metrics_provider
        self.services: Dict[str, Service] = {}
        self.databases: Dict[str, Database] = {}
        self.load_balancers: Dict[str, LoadBalancer] = {}
        self.workload: List[Dict[str, Any]] = self._load_workload()

    # ------------------------------------------------------------------
    def _load_workload(self) -> List[Dict[str, Any]]:
        if not self.workload_path.exists():
            return []
        try:
            with self.workload_path.open("r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:  # pragma: no cover - I/O errors
            return []

    # ------------------------------------------------------------------
    def add_service(self, service: Service) -> None:
        self.services[service.name] = service

    # ------------------------------------------------------------------
    def add_database(self, db: Database) -> None:
        self.databases[db.name] = db

    # ------------------------------------------------------------------
    def add_load_balancer(self, lb: LoadBalancer) -> None:
        self.load_balancers[lb.name] = lb

    # ------------------------------------------------------------------
    def step(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Return simulated state transition and metrics."""
        event = random.choice(self.workload) if self.workload else {}
        metrics = {"events_processed": len(self.workload)}
        if self.metrics_provider:
            metrics.update(self.metrics_provider.collect())
        return {"state": event, "metrics": metrics}
