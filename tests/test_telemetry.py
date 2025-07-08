import requests
from core.telemetry import setup_telemetry
from core.orchestrator import Orchestrator
from core.task import Task
from core.self_auditor import SelfAuditor
from unittest.mock import MagicMock


def test_setup_telemetry() -> None:
    server, _ = setup_telemetry(metrics_port=0)
    try:
        response = requests.get(f"http://localhost:{server.server_port}/metrics")
        assert response.status_code == 200
    finally:
        server.shutdown()


def test_tasks_executed_counter() -> None:
    server, _ = setup_telemetry(metrics_port=0)
    try:
        task = Task(id="1", description="d", component="c", dependencies=[], priority=1, status="pending")

        class DummyPlanner:
            def __init__(self):
                self.called = False

            def plan(self, tasks):
                if not self.called:
                    self.called = True
                    return tasks[0]
                return None

        class DummyExecutor:
            def execute(self, task):
                pass

        class DummyReflector:
            def run_cycle(self, tasks):
                return tasks

        memory = MagicMock()
        memory.load_tasks.return_value = [task]
        memory.save_tasks.return_value = None

        auditor = MagicMock(spec=SelfAuditor)
        auditor.audit.return_value = []

        orch = Orchestrator(DummyPlanner(), DummyExecutor(), DummyReflector(), memory, auditor)
        orch.run("tasks.yml")

        resp = requests.get(f"http://localhost:{server.server_port}/metrics")
        lines = [l for l in resp.text.splitlines() if l.startswith("tasks_executed_total")]
        assert lines and float(lines[0].split()[-1]) >= 1
    finally:
        server.shutdown()
