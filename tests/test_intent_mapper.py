import pytest
from core.intent_mapper import IntentMapper, Epic


def test_decompose_epic_creates_dependency_chain(task_factory):
    epic = Epic(id=1, title="E1", steps=["step1", "step2", "step3"])
    mapper = IntentMapper(default_priority=2)
    tasks = mapper.decompose_epic(epic, start_id=10)
    ids = [t.id for t in tasks]
    assert ids == [10, 11, 12]
    assert tasks[0].dependencies == []
    assert tasks[1].dependencies == [10]
    assert tasks[2].dependencies == [11]
    for t in tasks:
        assert t.epic == "E1"
        assert t.priority == 2
        assert t.status == "pending"


def test_map_goals_multiple_epics_produces_unique_ids():
    epic1 = Epic(id=1, title="E1", steps=["a", "b"])
    epic2 = Epic(id=2, title="E2", steps=["c"])
    mapper = IntentMapper()
    tasks = mapper.map_goals([epic1, epic2], start_id=1)
    ids = [t.id for t in tasks]
    assert ids == [1, 2, 3]
    assert tasks[1].dependencies == [1]
    assert tasks[2].dependencies == []
    assert tasks[0].epic == "E1"
    assert tasks[2].epic == "E2"
