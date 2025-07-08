from core.memory import Memory  # noqa: E402
from core.task import Task
import pytest
from jsonschema.exceptions import ValidationError
import yaml


def test_memory_load_save(tmp_path):
    path = tmp_path / "state.json"
    mem = Memory(path)
    data = {"hello": "world"}
    mem.save(data)
    assert path.exists()
    loaded = mem.load()
    assert loaded == data


def test_task_load_save_yaml(tmp_path):
    tasks = [
        Task(
            id=1,
            description="test",
            component="core",
            dependencies=[],
            priority=1,
            status="pending",
        )
    ]
    tasks_file = tmp_path / "tasks.yml"
    mem = Memory(tmp_path / "state.json")
    mem.save_tasks(tasks, tasks_file)
    loaded = mem.load_tasks(tasks_file)
    assert loaded == tasks


def test_task_validation_error(tmp_path):
    tasks_file = tmp_path / "tasks.yml"
    tasks_file.write_text("- id: 'one'\n")
    mem = Memory(tmp_path / "state.json")
    with pytest.raises(ValidationError):
        mem.load_tasks(tasks_file)


def test_save_tasks_omit_null_command(tmp_path):
    tasks = [
        Task(
            id=1,
            description="test command none",
            component="core",
            dependencies=[],
            priority=1,
            status="pending",
            command=None,
        )
    ]
    tasks_file = tmp_path / "tasks.yml"
    mem = Memory(tmp_path / "state.json")
    mem.save_tasks(tasks, tasks_file)
    data = yaml.safe_load(tasks_file.read_text())
    assert "command" not in data[0]


def test_task_round_trip_with_optional_fields(tmp_path):
    tasks = [
        Task(
            id=1,
            task_id="T-1",
            title="Extended",
            description="test optional",
            component="core",
            dependencies=[],
            priority=1,
            status="pending",
            area="core",
            actionable_steps=["a", "b"],
            acceptance_criteria=["c"],
            assigned_to="dev",
            epic="E1",
            metadata={"foo": "bar"},
        )
    ]
    tasks_file = tmp_path / "tasks.yml"
    mem = Memory(tmp_path / "state.json")
    mem.save_tasks(tasks, tasks_file)
    loaded = mem.load_tasks(tasks_file)
    assert loaded == tasks


def test_load_tasks_with_metadata(tmp_path):
    tasks_data = [
        {
            "id": 1,
            "description": "meta",
            "dependencies": [],
            "priority": 1,
            "status": "pending",
            "metadata": {"foo": "bar"},
        }
    ]
    tasks_file = tmp_path / "tasks.yml"
    tasks_file.write_text(yaml.safe_dump(tasks_data))
    mem = Memory(tmp_path / "state.json")
    tasks = mem.load_tasks(tasks_file)
    assert tasks == [
        Task(
            id=1,
            description="meta",
            dependencies=[],
            priority=1,
            status="pending",
            metadata={"foo": "bar"},
        )
    ]


def test_round_trip_extra_fields(tmp_path):
    tasks_data = [
        {
            "id": 1,
            "description": "extra",
            "dependencies": [],
            "priority": 1,
            "status": "pending",
            "foo": "bar",
            "nested": {"x": 1},
        }
    ]
    tasks_file = tmp_path / "tasks.yml"
    tasks_file.write_text(yaml.safe_dump(tasks_data))
    mem = Memory(tmp_path / "state.json")
    tasks = mem.load_tasks(tasks_file)
    assert tasks[0].metadata == {"foo": "bar", "nested": {"x": 1}}
    mem.save_tasks(tasks, tasks_file)
    round_tripped = yaml.safe_load(tasks_file.read_text())
    assert round_tripped[0]["foo"] == "bar"
    assert round_tripped[0]["nested"] == {"x": 1}


def test_invalid_metadata_fails(tmp_path):
    tasks_data = [
        {
            "id": 1,
            "description": "bad",
            "dependencies": [],
            "priority": 1,
            "status": "pending",
            "metadata": "not-a-dict",
        }
    ]
    tasks_file = tmp_path / "tasks.yml"
    tasks_file.write_text(yaml.safe_dump(tasks_data))
    mem = Memory(tmp_path / "state.json")
    with pytest.raises(ValidationError):
        mem.load_tasks(tasks_file)
