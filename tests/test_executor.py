import os
from pathlib import Path
import tempfile

def test_execute_task_with_description(executor, task_factory):
    """Logger should include the task description."""
    task = task_factory(id="t1", description="Task One Description")
    executor.execute(task)
    executor.logger.info.assert_called_once_with("Executing task: %s", "Task One Description")


def test_execute_task_with_id_no_description(executor, task_factory):
    """Fallback to task id when description is missing."""
    task = task_factory(id="t2")
    delattr(task, "description")
    executor.execute(task)
    executor.logger.info.assert_called_once_with("Executing task ID: %s (No description found)", "t2")


def test_execute_task_no_description_no_id(executor, task_factory):
    """Handle tasks lacking both description and id."""
    task = task_factory(id=0)
    delattr(task, "description")
    delattr(task, "id")
    executor.execute(task)
    executor.logger.info.assert_called_once_with("Executing task: (No description or ID found)")


def test_execute_task_as_dict_with_description(executor, task_factory):
    """Task dataclass mimics attribute access for mapping inputs."""
    task = task_factory(id="d1", description="Dict Task Description")
    executor.execute(task)
    executor.logger.info.assert_called_once_with("Executing task: %s", "Dict Task Description")


def test_execute_task_as_dict_with_id_no_description(executor, task_factory):
    task = task_factory(id="d2")
    delattr(task, "description")
    executor.execute(task)
    executor.logger.info.assert_called_once_with("Executing task ID: %s (No description found)", "d2")


def test_execute_task_object_with_other_attributes(executor, task_factory):
    task = task_factory(id="t_other", description="Other attributes test", priority=10)
    executor.execute(task)
    executor.logger.info.assert_called_once_with("Executing task: %s", "Other attributes test")


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

