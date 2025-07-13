import os
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

os.environ.setdefault("TEMPORARILY_DISABLE_PROTOBUF_VERSION_CHECK", "true")
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import core.bridge_pb2 as _bridge_pb2
sys.modules.setdefault("bridge_pb2", _bridge_pb2)
import core.bridge_pb2_grpc as _bridge_pb2_grpc
sys.modules.setdefault("bridge_pb2_grpc", _bridge_pb2_grpc)

from core.executor import Executor
from core.planner import Planner
from core.task import Task


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "integration: mark test that requires external services"
    )


def pytest_collection_modifyitems(config, items):
    if config.getoption("--run-integration"):
        return
    skip_integration = pytest.mark.skip(reason="integration test skipped")
    for item in items:
        if "integration" in item.keywords:
            item.add_marker(skip_integration)

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
            "cost": 1,
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


def pytest_addoption(parser):
    parser.addoption(
        "--run-integration",
        action="store_true",
        default=False,
        help="run tests marked as integration",
    )
