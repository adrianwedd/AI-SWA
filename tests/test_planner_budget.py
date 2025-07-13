import pytest
from core.planner import Planner
from core.task import Task


def make_task(id: str, priority: int = 1, cost: int = 1):
    return Task(id=id, description="", dependencies=[], priority=priority, status="pending", cost=cost)


def test_budget_warning(caplog):
    planner = Planner(budget=3, warning_threshold=0.66)
    tasks = [make_task("t1"), make_task("t2"), make_task("t3")]
    with caplog.at_level("WARNING"):
        first = planner.plan(tasks)
        assert first.id == "t1"
        assert "budget" not in caplog.text
        first.status = "done"
        assert planner.plan(tasks).id == "t2"
        assert "budget" in caplog.text


def test_budget_exhaustion():
    planner = Planner(budget=1)
    tasks = [make_task("t1"), make_task("t2")]
    assert planner.plan(tasks).id == "t1"
    assert planner.plan(tasks) is None


def test_refuse_over_budget_task():
    planner = Planner(budget=3)
    tasks = [
        make_task("t1", cost=2),
        make_task("t2", cost=2),
    ]
    assert planner.plan(tasks).id == "t1"
    assert planner.plan(tasks) is None

