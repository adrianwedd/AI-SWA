from simulator.code_env import CodeEnv, Service, Database, LoadBalancer
from core.task import Task


def test_code_env_step_and_task_queue(tmp_path):
    workload = tmp_path / "workload.json"
    workload.write_text('[{"service": "api", "database": "db"}]')
    env = CodeEnv(workload_path=workload)
    env.add_service(Service(name="api", capacity=1))
    env.add_database(Database(name="db", max_connections=1))
    env.add_load_balancer(LoadBalancer(name="lb", targets=[env.simulator.services["api"]]))

    task = Task(id=1, description="test", dependencies=[], priority=1, status="pending")
    env.submit_task(task)
    assert env.next_task() is task

    result = env.step({})
    assert result["metrics"]["events_processed"] == 1
