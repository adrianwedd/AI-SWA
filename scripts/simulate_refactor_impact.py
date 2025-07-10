"""Simulate system behavior and collect metrics for pending refactor tasks."""

from __future__ import annotations

import argparse
from pathlib import Path
import json
import yaml

from core.self_auditor import SelfAuditor
from core.production_simulator import ProductionSimulator, Service, Database, LoadBalancer


def collect_refactor_files(tasks_path: Path) -> list[Path]:
    tasks = yaml.safe_load(tasks_path.read_text())
    files = []
    for task in tasks:
        desc = task.get("description", "")
        if task.get("status") == "pending" and desc.startswith("Refactor"):
            parts = desc.split()
            if len(parts) > 1 and parts[1].endswith(".py"):
                files.append(Path(parts[1]))
    return files


def analyze_files(files: list[Path]) -> dict[str, dict]:
    auditor = SelfAuditor()
    return auditor.analyze(files)


def run_simulation(workload: Path, steps: int = 1) -> dict:
    sim = ProductionSimulator(workload_path=workload)
    sim.add_service(Service(name="api", capacity=10))
    sim.add_database(Database(name="db", max_connections=5))
    sim.add_load_balancer(LoadBalancer(name="lb", targets=[sim.services["api"]]))
    for _ in range(steps):
        sim.step({})
    return sim.collect_metrics()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tasks", type=Path, default=Path("tasks.yml"))
    parser.add_argument("--workload", type=Path, default=Path("workload.json"))
    parser.add_argument("--steps", type=int, default=1)
    args = parser.parse_args()

    refactor_files = collect_refactor_files(args.tasks)
    if refactor_files:
        metrics = analyze_files(refactor_files)
    else:
        metrics = {}

    if not args.workload.exists():
        args.workload.write_text(json.dumps([{"service": "api", "database": "db"}]))

    sim_metrics = run_simulation(args.workload, args.steps)

    print(json.dumps({"code_metrics": metrics, "simulation_metrics": sim_metrics}, indent=2))


if __name__ == "__main__":  # pragma: no cover
    main()
