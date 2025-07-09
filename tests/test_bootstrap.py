import subprocess
import sys
import logging
from pathlib import Path
import pytest

from core.bootstrap import (
    load_schema_and_tasks,
    create_logfile_path,
    setup_logging,
    select_next_task,
)
from core.memory import TASK_SCHEMA


@pytest.mark.parametrize(
    "check",
    [
        lambda: Path("ARCHITECTURE.md").exists(),
        lambda: Path("tasks.yml").exists(),
        lambda: Path("requirements.txt").exists(),
        lambda: Path("AGENTS.md").exists(),
        lambda: list(Path("logs").glob("bootstrap-*.log")),
    ],
)
def test_artifacts_and_log(check):
    """Essential repository files and bootstrap log should exist."""
    assert check()


@pytest.mark.parametrize(
    "content, code",
    [
        (None, 2),
        ("# jsonschema:\n# { invalid }", 1),
    ],
)
def test_bootstrap_exit_codes(tmp_path, root_path, content, code):
    """Verify bootstrap exit codes for missing or invalid tasks."""
    if content is not None:
        (tmp_path / "tasks.yml").write_text(content)
    result = subprocess.run(
        [sys.executable, str(root_path / "core" / "bootstrap.py")],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert result.returncode == code


@pytest.mark.parametrize(
    "content, expected_schema",
    [
        (
            "# jsonschema:\n"
            "# {\"type\": \"array\"}\n"
            "- id: 1\n"
            "  description: test\n"
            "  component: core\n"
            "  dependencies: []\n"
            "  priority: 1\n"
            "  status: pending\n",
            {"type": "array"},
        ),
        (
            "- id: 1\n"
            "  description: test\n"
            "  component: core\n"
            "  dependencies: []\n"
            "  priority: 1\n"
            "  status: pending\n",
            TASK_SCHEMA,
        ),
    ],
)
def test_load_schema_and_tasks(tmp_path, content, expected_schema):
    """Parse schema header and tasks from file."""
    path = tmp_path / "tasks.yml"
    path.write_text(content)
    schema, tasks = load_schema_and_tasks(path)
    assert schema == expected_schema and tasks[0]["id"] == 1


def test_logfile_utilities(tmp_path):
    """Ensure logfile helpers create files correctly."""
    logging.getLogger().handlers.clear()
    path = create_logfile_path(tmp_path)
    logfile = setup_logging(base_dir=tmp_path)
    logging.info("create")
    assert (
        path.parent,
        path.name.startswith("bootstrap-"),
        path.suffix,
        logfile.exists(),
    ) == (tmp_path, True, ".log", True)


@pytest.mark.parametrize(
    "tasks, expected",
    [
        (
            [
                {"id": 1, "status": "done"},
                {"id": 2, "status": "pending", "priority": 2},
                {"id": 3, "status": "pending", "priority": 1},
            ],
            3,
        ),
        ([{"id": 1, "status": "done"}], None),
    ],
)
def test_select_next_task(tasks, expected):
    """Select the pending task with the highest priority or ``None``."""
    result = select_next_task(tasks)
    assert (result["id"] if result else None) == expected
