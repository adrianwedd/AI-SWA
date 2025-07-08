import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.executor import Executor
from core.planner import Planner
from core.task import Task


@pytest.fixture(scope="session", autouse=True)
def add_project_root_to_sys_path():
    yield
    if str(ROOT) in sys.path:
        sys.path.remove(str(ROOT))


@pytest.fixture
def root_path():
    """Return repository root path."""
    return ROOT


@pytest.fixture
def task_factory():
    """Factory for :class:`~core.task.Task` with sensible defaults."""

    def _factory(**overrides):
        defaults = {
            "id": "t",
            "description": "A task",
            "component": "test",
            "dependencies": [],
            "priority": 1,
            "status": "pending",
        }
        defaults.update(overrides)
        return Task(**defaults)

    return _factory


@pytest.fixture
def executor():
    """Return :class:`~core.executor.Executor` with mocked logger."""
    exe = Executor()
    exe.logger = MagicMock()
    return exe


@pytest.fixture
def planner():
    """Return a new :class:`~core.planner.Planner`."""
    return Planner()
