import json
from unittest.mock import MagicMock, patch
from pathlib import Path
from core.sentinel import EthicalSentinel
from core.orchestrator import Orchestrator
from core.task import Task
from core.planner import Planner
from core.executor import Executor
from core.reflector import Reflector
from core.memory import Memory
from core.self_auditor import SelfAuditor


def test_policy_loading_and_blocking(tmp_path: Path):
    policy = tmp_path / "policy.json"
    policy.write_text(json.dumps({"blocked_actions": ["block"]}))
    sentinel = EthicalSentinel(policy)

    task = Task(id="block", description="", component="core", dependencies=[], priority=1, status="pending")

    memory = MagicMock(spec=Memory)
    memory.load_tasks.return_value = [task]
    memory.save_tasks.return_value = None

    planner = MagicMock(spec=Planner)
    planner.plan.side_effect = [task, None]

    reflector = MagicMock(spec=Reflector)
    reflector.run_cycle.return_value = [task]

    auditor = MagicMock(spec=SelfAuditor)
    auditor.audit.return_value = []

    executor = MagicMock(spec=Executor)
    orch = Orchestrator(planner, executor, reflector, memory, auditor, sentinel=sentinel)

    orch.logger = MagicMock()
    message = "Orchestrator: Task 'block' blocked by Ethical Sentinel."

    with patch('builtins.print') as mock_print:
        orch.run("tasks.yml")

    assert sentinel.blocked_actions == {"block"}
    mock_print.assert_any_call(message)
    orch.logger.info.assert_called_with(message)
    # Executor should not be called because sentinel blocks the action
    executor.execute.assert_not_called()
