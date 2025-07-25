"""Simplified simulation of the production environment for RL training."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Any
import json
import random
from copy import deepcopy

from .observability import MetricsProvider


@dataclass
class Service:
    """Represents a core service in the production environment."""

    name: str
    capacity: int
    latency_ms: int = 0
    requests_handled: int = 0

    def handle_request(self) -> int:
        """Simulate handling a request and return latency."""
        if self.requests_handled < self.capacity:
            self.requests_handled += 1
        return self.latency_ms


@dataclass
class Database:
    """Represents a backing database."""

    name: str
    max_connections: int
    active_connections: int = 0

    def connect(self) -> bool:
        if self.active_connections >= self.max_connections:
            return False
        self.active_connections += 1
        return True

    def disconnect(self) -> None:
        if self.active_connections > 0:
            self.active_connections -= 1


@dataclass
class LoadBalancer:
    """Simple load balancer distributing requests across services."""

    name: str
    targets: List[Service] = field(default_factory=list)
    _index: int = 0

    def route_request(self) -> Optional[Service]:
        if not self.targets:
            return None
        service = self.targets[self._index % len(self.targets)]
        self._index += 1
        service.handle_request()
        return service


class SimulationMetricsProvider(MetricsProvider):
    """Expose ``ProductionSimulator`` metrics via ``MetricsProvider``."""

    def __init__(self, simulator: "ProductionSimulator") -> None:
        super().__init__(metrics_path=None)
        self.simulator = simulator

    def collect(self) -> Dict[str, Any]:
        return self.simulator.collect_metrics()


class ProductionSimulator:
    """High-level simulator mirroring production behavior."""

    def __init__(
        self,
        workload_path: Path,
        metrics_provider: Optional[MetricsProvider] = None,
        seed: Optional[int] = None,
    ) -> None:
        self.workload_path = Path(workload_path)
        self.metrics_provider = metrics_provider
        self.random = random.Random(seed)
        self.services: Dict[str, Service] = {}
        self.databases: Dict[str, Database] = {}
        self.load_balancers: Dict[str, LoadBalancer] = {}
        self.workload: List[Dict[str, Any]] = self._load_workload()
        self._cursor = 0
        self._metrics: Dict[str, Any] = {"events_processed": 0}
        self._seed = seed

    # ------------------------------------------------------------------
    def reset(self) -> None:
        """Reset simulator state for a reproducible run."""
        self.random = random.Random(self._seed)
        self.workload = self._load_workload()
        self._cursor = 0
        self._metrics = {"events_processed": 0}

    # ------------------------------------------------------------------
    def snapshot(self) -> Dict[str, Any]:
        """Return a snapshot of the simulator state."""
        return {
            "cursor": self._cursor,
            "metrics": deepcopy(self._metrics),
            "services": {n: s.requests_handled for n, s in self.services.items()},
            "databases": {n: d.active_connections for n, d in self.databases.items()},
            "load_balancers": {n: lb._index for n, lb in self.load_balancers.items()},
        }

    # ------------------------------------------------------------------
    def restore(self, state: Dict[str, Any]) -> None:
        """Restore simulator state from ``state``."""
        self._cursor = state.get("cursor", 0)
        self._metrics = deepcopy(state.get("metrics", {"events_processed": 0}))
        for name, count in state.get("services", {}).items():
            if name in self.services:
                self.services[name].requests_handled = count
        for name, count in state.get("databases", {}).items():
            if name in self.databases:
                self.databases[name].active_connections = count
        for name, idx in state.get("load_balancers", {}).items():
            if name in self.load_balancers:
                self.load_balancers[name]._index = idx

    # ------------------------------------------------------------------
    def _load_workload(self) -> List[Dict[str, Any]]:
        if not self.workload_path.exists():
            return []
        try:
            with self.workload_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            events = data if isinstance(data, list) else []
            self.random.shuffle(events)
            return events
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
    def apply_action(self, action: Dict[str, Any]) -> None:
        """Apply an action modifying simulator state."""
        scale = action.get("scale_service")
        if scale:
            svc = self.services.get(scale.get("name"))
            if svc:
                svc.capacity += int(scale.get("delta", 0))

        latency = action.get("set_latency")
        if latency:
            svc = self.services.get(latency.get("name"))
            if svc:
                svc.latency_ms = int(latency.get("latency_ms", svc.latency_ms))

    # ------------------------------------------------------------------
    def collect_metrics(self) -> Dict[str, Any]:
        metrics = {"events_processed": self._metrics["events_processed"]}
        for name, svc in self.services.items():
            metrics[f"{name}_handled"] = svc.requests_handled
        for name, db in self.databases.items():
            metrics[f"{name}_active"] = db.active_connections
        return metrics

    # ------------------------------------------------------------------
    def step(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Return simulated state transition and metrics."""
        self.apply_action(action)
        if not self.workload:
            event = {}
        else:
            event = self.workload[self._cursor]
            self._cursor = (self._cursor + 1) % len(self.workload)

        svc_name = event.get("service")
        db_name = event.get("database")

        if svc_name in self.load_balancers:
            self.load_balancers[svc_name].route_request()
        elif svc_name in self.services:
            self.services[svc_name].handle_request()

        if db_name and db_name in self.databases and self.databases[db_name].connect():
            self.databases[db_name].disconnect()

        self._metrics["events_processed"] += 1
        metrics = self.collect_metrics()
        if self.metrics_provider and not isinstance(self.metrics_provider, SimulationMetricsProvider):
            metrics.update(self.metrics_provider.collect())
        return {"state": event, "metrics": metrics}
