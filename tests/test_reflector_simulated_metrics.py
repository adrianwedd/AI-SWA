import yaml

from core.reflector import Reflector
from core.production_simulator import (
    ProductionSimulator,
    Service,
    Database,
    LoadBalancer,
    SimulationMetricsProvider,
)
from core.cicd_simulator import CICDSimulator, BuildJob
from core.observability import MetricsProvider


class CombinedProvider(MetricsProvider):
    def __init__(self, prod: ProductionSimulator, cicd: CICDSimulator):
        super().__init__(metrics_path=None)
        self.prod = prod
        self.cicd = cicd

    def collect(self):
        metrics = {}
        metrics.update(self.prod.collect_metrics())
        metrics.update(self.cicd.collect_metrics())
        total_builds = metrics.get("successful_builds", 0) + metrics.get("failed_builds", 0)
        if total_builds:
            metrics["coverage"] = metrics["successful_builds"] / total_builds * 100
        else:
            metrics["coverage"] = 100
        metrics["dependency_health"] = "outdated" if metrics.get("events_processed", 0) else "healthy"
        metrics["complexity_history"] = [10, 20]
        return metrics


def test_reflector_decisions_with_simulated_metrics(tmp_path):
    workload = tmp_path / "workload.json"
    workload.write_text('[{"service": "api", "database": "db"}]')
    prod = ProductionSimulator(workload_path=workload)
    prod.add_service(Service(name="api", capacity=1))
    prod.add_database(Database(name="db", max_connections=1))
    prod.add_load_balancer(LoadBalancer(name="lb", targets=[prod.services["api"]]))
    prod.step({})

    cicd = CICDSimulator()
    cicd.add_job(BuildJob(risk=1.0))
    cicd.step({})

    provider = CombinedProvider(prod, cicd)

    tasks_file = tmp_path / "tasks.yml"
    tasks_file.write_text(
        "- id: 1\n  description: base\n  component: core\n  dependencies: []\n  priority: 1\n  status: pending\n"
    )
    code_file = tmp_path / "code.py"
    code_file.write_text("def foo():\n    return 1\n")
    tasks = yaml.safe_load(tasks_file.read_text())

    refl = Reflector(tasks_path=tasks_file, analysis_paths=[code_file], metrics_provider=provider)
    analysis = refl.analyze()
    decisions = refl.decide(analysis, tasks)
    assert any(d.get("reason") == "Low test coverage" for d in decisions["process_improvements"])
    assert any(d.get("reason") == "outdated_dependencies" for d in decisions["architectural_improvements"])
