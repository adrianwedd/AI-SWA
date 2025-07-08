import requests
import pytest
from core.telemetry import setup_telemetry
from core.orchestrator import Orchestrator
from core.task import Task
from core.self_auditor import SelfAuditor
from unittest.mock import MagicMock


@pytest.fixture
def telemetry_server():
    from opentelemetry.metrics import _internal as metrics_internal
    from opentelemetry import trace as trace_api

    metrics_internal._METER_PROVIDER_SET_ONCE._done = False
    metrics_internal._METER_PROVIDER = None
    trace_api._TRACER_PROVIDER_SET_ONCE._done = False
    trace_api._TRACER_PROVIDER = None

    server, _ = setup_telemetry(metrics_port=0)
    yield server
    server.shutdown()


def test_setup_telemetry(telemetry_server) -> None:
    response = requests.get(
        f"http://localhost:{telemetry_server.server_port}/metrics"
    )
    assert response.status_code == 200


def test_tasks_executed_metric(telemetry_server, tmp_path):
    from core.orchestrator import Orchestrator
    from core.task import Task
    from unittest.mock import MagicMock

    task = Task(
        id="1",
        description="",
        component="core",
        dependencies=[],
        priority=1,
        status="pending",
    )

    memory = MagicMock()
    memory.load_tasks.return_value = [task]
    planner = MagicMock()
    planner.plan.side_effect = [task, None]
    reflector = MagicMock()
    reflector.run_cycle.return_value = [task]
    executor = MagicMock()
    auditor = MagicMock()
    auditor.audit.return_value = []

    orch = Orchestrator(planner, executor, reflector, memory, auditor)

    def fetch_count() -> float:
        resp = requests.get(
            f"http://localhost:{telemetry_server.server_port}/metrics"
        )
        for line in resp.text.splitlines():
            if line.startswith("tasks_executed_total"):
                return float(line.split()[-1])
        return 0.0

    orch.run(str(tmp_path / "tasks.yml"))
    after = fetch_count()

    assert after == 1.0

