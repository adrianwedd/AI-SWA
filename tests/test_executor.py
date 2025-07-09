import os
from pathlib import Path
import tempfile
import pytest


@pytest.mark.parametrize(
    "task_kwargs, remove_desc, remove_id, expected",
    [
        ({"id": "t1", "description": "Task One Description"}, False, False,
         ("Executing task: %s", "Task One Description")),
        ({"id": "d1", "description": "Dict Task Description"}, False, False,
         ("Executing task: %s", "Dict Task Description")),
        ({"id": "t_other", "description": "Other attributes test", "priority": 10}, False, False,
         ("Executing task: %s", "Other attributes test")),
        ({"id": "t2"}, True, False,
         ("Executing task ID: %s (No description found)", "t2")),
        ({"id": "d2"}, True, False,
         ("Executing task ID: %s (No description found)", "d2")),
        ({"id": 0}, True, True,
         ("Executing task: (No description or ID found)",)),
    ],
)
def test_execute_task_logging(executor, task_factory, task_kwargs, remove_desc, remove_id, expected):
    """Executor logs correct messages for various task definitions."""
    task = task_factory(**task_kwargs)
    if remove_desc:
        delattr(task, "description")
    if remove_id:
        delattr(task, "id")

    executor.execute(task)
    executor.logger.info.assert_called_once_with(*expected)


def test_execute_task_with_command_creates_log(executor, task_factory):
    task = task_factory(id="cmd", description="Run echo", command="echo 'hello there'")
    with tempfile.TemporaryDirectory() as tmpdir:
        cwd = Path.cwd()
        Path(tmpdir).mkdir(exist_ok=True)
        try:
            Path.cwd().joinpath(tmpdir)
            os.chdir(tmpdir)
            executor.execute(task)
        finally:
            os.chdir(cwd)
        logs = list(Path(tmpdir, "logs").glob("task-cmd-*.log"))
        assert logs and logs[0].read_text().strip() == "hello there"

