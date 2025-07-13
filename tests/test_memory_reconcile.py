from pathlib import Path
from core.task import Task
from core.memory import Memory


def test_reconcile_prefers_high_score(tmp_path):
    mem = Memory(Path(tmp_path / "state.json"))
    old = Task(id=1, description="old", dependencies=[], priority=1, status="done")
    new = Task(id=1, description="new", dependencies=[], priority=1, status="done")
    result = mem.reconcile_tasks([old], [new], {1: {"existing": 3, "new": 7}})
    assert result[0].description == "new"


def test_reconcile_keeps_existing_when_score_higher(tmp_path):
    mem = Memory(Path(tmp_path / "state.json"))
    old = Task(id=1, description="old", dependencies=[], priority=1, status="done")
    new = Task(id=1, description="new", dependencies=[], priority=1, status="done")
    result = mem.reconcile_tasks([old], [new], {1: {"existing": 9, "new": 2}})
    assert result[0].description == "old"


def test_reconcile_merges_by_description(tmp_path):
    mem = Memory(Path(tmp_path / "state.json"))
    old = Task(id=1, description="refactor foo", dependencies=[1], priority=1, status="pending")
    new = Task(id=2, description="refactor foo", dependencies=[2], priority=3, status="pending")
    result = mem.reconcile_tasks([old], [new], {1: {"existing": 5}, 2: {"new": 6}})
    assert len(result) == 1
    merged = result[0]
    assert merged.priority == 3
    assert set(merged.dependencies) == {1, 2}

