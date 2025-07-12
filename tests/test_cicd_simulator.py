from core.cicd_simulator import CICDSimulator, BuildJob


def test_cicd_simulator_step():
    sim = CICDSimulator()
    sim.add_job(BuildJob(risk=0.0))
    result = sim.step({})
    metrics = result["metrics"]
    assert metrics["successful_builds"] == 1
    assert metrics["queued_jobs"] == 0

