import subprocess
import sys
import logging
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

from core.bootstrap import (
    load_schema_and_tasks,
    create_logfile_path,
    setup_logging,
    select_next_task,
)
from core.memory import TASK_SCHEMA


def test_artifacts_exist():
    required = [
        "ARCHITECTURE.md",
        "tasks.yml",
        "requirements.txt",
        "AGENTS.md",
    ]
    for fname in required:
        assert Path(fname).exists(), f"{fname} not found"


def test_log_created():
    logs = list(Path("logs").glob("bootstrap-*.log"))
    assert logs, "No bootstrap log found"


def test_missing_tasks_file(tmp_path):
    result = subprocess.run(
        [sys.executable, str(ROOT / "core" / "bootstrap.py")],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2


def test_schema_error(tmp_path):
    (tmp_path / "tasks.yml").write_text("# jsonschema:\n# { invalid }")
    result = subprocess.run(
        [sys.executable, str(ROOT / "core" / "bootstrap.py")],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1


def test_load_schema_and_tasks(tmp_path):
    content = (
        "# jsonschema:\n"
        "# {\"type\": \"array\"}\n"
        "- id: 1\n"
        "  description: test\n"
        "  component: core\n"
        "  dependencies: []\n"
        "  priority: 1\n"
        "  status: pending\n"
    )
    path = tmp_path / "tasks.yml"
    path.write_text(content)
    schema, tasks = load_schema_and_tasks(path)
    assert schema["type"] == "array"
    assert tasks[0]["id"] == 1


def test_load_schema_and_tasks_without_header(tmp_path):
    content = (
        "- id: 1\n"
        "  description: test\n"
        "  component: core\n"
        "  dependencies: []\n"
        "  priority: 1\n"
        "  status: pending\n"
    )
    path = tmp_path / "tasks.yml"
    path.write_text(content)
    schema, tasks = load_schema_and_tasks(path)
    assert schema == TASK_SCHEMA
    assert tasks[0]["id"] == 1


def test_create_logfile_path(tmp_path):
    logfile = create_logfile_path(tmp_path)
    assert logfile.parent == tmp_path
    assert logfile.name.startswith("bootstrap-") and logfile.suffix == ".log"


def test_setup_logging_creates_file(tmp_path):
    logging.getLogger().handlers.clear()
    logfile = setup_logging(base_dir=tmp_path)
    logging.info("create")
    assert logfile.exists()


def test_select_next_task():
    tasks = [
        {"id": 1, "status": "done"},
        {"id": 2, "status": "pending", "priority": 2},
        {"id": 3, "status": "pending", "priority": 1},
    ]
    next_task = select_next_task(tasks)
    assert next_task["id"] == 3


def test_select_next_task_none():
    tasks = [{"id": 1, "status": "done"}]
    assert select_next_task(tasks) is None
