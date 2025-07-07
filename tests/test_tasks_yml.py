import json
import yaml
from pathlib import Path
from jsonschema import validate
from core.memory import Memory, TASK_SCHEMA

ROOT = Path(__file__).resolve().parents[1]


def test_tasks_file_starts_with_schema_comment():
    tasks_file = ROOT / "tasks.yml"
    with tasks_file.open() as f:
        first_line = f.readline().strip()
    assert first_line.startswith(
        "# jsonschema:"
    ), "tasks.yml must start with jsonschema comment block"


def test_task_ids_unique():
    tasks_file = ROOT / "tasks.yml"
    with tasks_file.open() as f:
        tasks = yaml.safe_load(f)
    ids = [task["id"] for task in tasks]
    assert len(ids) == len(set(ids)), "Task IDs must be unique"


def test_tasks_yml_validates_against_schema():
    tasks_file = ROOT / "tasks.yml"
    text = tasks_file.read_text().splitlines()
    schema_lines = []
    task_lines = []
    schema_started = False
    for line in text:
        if line.startswith("# jsonschema:"):
            schema_started = True
            continue
        if schema_started and line.startswith("#"):
            schema_lines.append(line[1:].lstrip())
            continue
        task_lines.append(line)
    schema = TASK_SCHEMA if not schema_lines else json.loads("\n".join(schema_lines))
    tasks = yaml.safe_load("\n".join(task_lines))
    validate(instance=tasks, schema=schema)


def test_tasks_round_trip_preserves_optional_fields(tmp_path):
    tasks_file = ROOT / "tasks.yml"
    mem = Memory(tmp_path / "state.json")
    tasks = mem.load_tasks(tasks_file)
    out = tmp_path / "out.yml"
    mem.save_tasks(tasks, out)
    loaded = mem.load_tasks(out)
    assert tasks == loaded
