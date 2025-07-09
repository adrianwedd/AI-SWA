import pytest
from unittest.mock import MagicMock, patch
from core.task import Task
from core.orchestrator import Orchestrator


def make_orchestrator(mem=None, planner=None, executor=None, reflector=None, auditor=None, sentinel=None):
    mem = mem or MagicMock()
    planner = planner or MagicMock()
    executor = executor or MagicMock()
    reflector = reflector or MagicMock()
    auditor = auditor or MagicMock()
    auditor.audit.return_value = []
    return Orchestrator(planner, executor, reflector, mem, auditor, sentinel)


def test_load_tasks_exception_logged():
    mem = MagicMock()
    mem.load_tasks.side_effect = ValueError("boom")
    orch = make_orchestrator(mem=mem)
    orch.logger = MagicMock()
    orch.planner.plan.return_value = None
    orch.reflector.run_cycle.return_value = []
    with patch("builtins.print"):
        orch.run("tasks.yml")
    orch.logger.exception.assert_called_once()


def test_save_tasks_exception_logged():
    task = Task(id="t1", description="d", component="c", dependencies=[], priority=1, status="pending")
    mem = MagicMock()
    mem.load_tasks.return_value = [task]
    mem.save_tasks.side_effect = IOError("disk")
    orch = make_orchestrator(mem=mem)
    orch.logger = MagicMock()
    orch.planner.plan.side_effect = [task, None]
    orch.reflector.run_cycle.return_value = [task]
    with patch("builtins.print"):
        orch.run("tasks.yml")
    assert orch.logger.exception.call_args_list


def test_audit_failure_logged():
    task = Task(id="t1", description="d", component="c", dependencies=[], priority=1, status="pending")
    mem = MagicMock()
    mem.load_tasks.return_value = [task]
    mem.save_tasks.return_value = None
    auditor = MagicMock()
    auditor.audit.side_effect = RuntimeError("bad")
    orch = make_orchestrator(mem=mem, auditor=auditor)
    orch.logger = MagicMock()
    orch.planner.plan.side_effect = [task, None]
    orch.reflector.run_cycle.return_value = [task]
    with patch("builtins.print"):
        orch.run("tasks.yml")
    orch.logger.exception.assert_called_once()


def test_sentinel_blocks_execution():
    task = Task(id="block", description="d", component="c", dependencies=[], priority=1, status="pending")
    mem = MagicMock()
    mem.load_tasks.return_value = [task]
    mem.save_tasks.return_value = None
    sentinel = MagicMock()
    sentinel.allows.return_value = False
    orch = make_orchestrator(mem=mem, sentinel=sentinel)
    orch.logger = MagicMock()
    orch.planner.plan.side_effect = [task, None]
    orch.reflector.run_cycle.return_value = [task]
    with patch("builtins.print"):
        orch.run("tasks.yml")
    orch.executor.execute.assert_not_called()
