from core.production_simulator import (
    ProductionSimulator,
    Service,
    Database,
    LoadBalancer,
    SimulationMetricsProvider,
)


def test_simulator_step(tmp_path):
    workload = tmp_path / "workload.json"
    workload.write_text('[{"service": "api", "database": "db"}]')
    sim = ProductionSimulator(workload_path=workload)
    sim.add_service(Service(name="api", capacity=2))
    sim.add_database(Database(name="db", max_connections=1))
    sim.add_load_balancer(LoadBalancer(name="lb", targets=[sim.services["api"]]))
    sim.metrics_provider = SimulationMetricsProvider(sim)
    result = sim.step({})
    assert result["state"] == {"service": "api", "database": "db"}
    assert result["metrics"]["events_processed"] == 1
    assert result["metrics"]["api_handled"] == 1


def test_simulator_reproducibility(tmp_path):
    workload = tmp_path / "workload.json"
    workload.write_text('[{"service": "api"}, {"service": "worker"}]')
    sim1 = ProductionSimulator(workload_path=workload, seed=42)
    sim1.add_service(Service(name="api", capacity=1))
    sim1.add_service(Service(name="worker", capacity=1))

    sim2 = ProductionSimulator(workload_path=workload, seed=42)
    sim2.add_service(Service(name="api", capacity=1))
    sim2.add_service(Service(name="worker", capacity=1))

    out1 = [sim1.step({})["state"] for _ in range(2)]
    out2 = [sim2.step({})["state"] for _ in range(2)]
    assert out1 == out2
