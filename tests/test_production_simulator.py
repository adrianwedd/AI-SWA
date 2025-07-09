from core.production_simulator import ProductionSimulator, Service, Database, LoadBalancer


def test_simulator_step(tmp_path):
    workload = tmp_path / "workload.json"
    workload.write_text('[{"event": "req"}]')
    sim = ProductionSimulator(workload_path=workload)
    sim.add_service(Service(name="api", capacity=10))
    sim.add_database(Database(name="db", max_connections=5))
    sim.add_load_balancer(LoadBalancer(name="lb", targets=[sim.services["api"]]))
    result = sim.step({})
    assert "state" in result
    assert "metrics" in result
