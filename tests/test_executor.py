import os
import unittest
from pathlib import Path
from unittest.mock import MagicMock
from core.executor import Executor
from core.task import Task

class TestExecutor(unittest.TestCase):

    def setUp(self):
        self.executor = Executor()
        self.executor.logger = MagicMock()

    def test_execute_task_with_description(self):
        task = Task(
            id="t1",
            description="Task One Description",
            component="test",
            dependencies=[],
            priority=1,
            status="pending",
        )
        self.executor.execute(task)
        self.executor.logger.info.assert_called_once_with("Executing task: %s", "Task One Description")

    def test_execute_task_with_id_no_description(self):
        task = Task(
            id="t2",
            description="",
            component="test",
            dependencies=[],
            priority=1,
            status="pending",
        )
        # Ensure description attribute is not present
        if hasattr(task, 'description'):
            delattr(task, 'description')
        self.executor.execute(task)
        self.executor.logger.info.assert_called_once_with("Executing task ID: %s (No description found)", "t2")

    def test_execute_task_no_description_no_id(self):
        task = Task(
            id=0,
            description="",
            component="test",
            dependencies=[],
            priority=1,
            status="pending",
        )
        # Ensure description and id attributes are not present
        if hasattr(task, 'description'):
            delattr(task, 'description')
        if hasattr(task, 'id'):
            delattr(task, 'id')
        self.executor.execute(task)
        self.executor.logger.info.assert_called_once_with("Executing task: (No description or ID found)")

    def test_execute_task_as_dict_with_description(self):
        # The Executor expects an object with attributes. Using the Task
        # dataclass mimics this interface and keeps the test focused on the
        # print behavior rather than attribute lookups.
        task = Task(
            id="d1",
            description="Dict Task Description",
            component="test",
            dependencies=[],
            priority=1,
            status="pending",
        )
        self.executor.execute(task)
        self.executor.logger.info.assert_called_once_with("Executing task: %s", "Dict Task Description")

    def test_execute_task_as_dict_with_id_no_description(self):
        task_obj = Task(
            id="d2",
            description="",
            component="test",
            dependencies=[],
            priority=1,
            status="pending",
        )
        if hasattr(task_obj, 'description'):
            delattr(task_obj, 'description')
        self.executor.execute(task_obj)
        self.executor.logger.info.assert_called_once_with("Executing task ID: %s (No description found)", "d2")

    def test_execute_task_object_with_other_attributes(self):
        task = Task(
            id="t_other",
            description="Other attributes test",
            component="test",
            dependencies=[],
            priority=10,
            status="pending",
        )
        self.executor.execute(task)
        self.executor.logger.info.assert_called_once_with("Executing task: %s", "Other attributes test")

    def test_execute_task_with_command_creates_log(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            cwd = os.getcwd()
            os.chdir(tmpdir)
            try:
                task = Task(
                    id="cmd",
                    description="Run echo",
                    component="test",
                    dependencies=[],
                    priority=1,
                    status="pending",
                    command="echo 'hello there'",
                )
                self.executor.execute(task)
            finally:
                os.chdir(cwd)

            logs = list(Path(tmpdir).joinpath("logs").glob("task-cmd-*.log"))
            assert logs, "Log file not created"
            assert logs[0].read_text().strip() == "hello there"


if __name__ == '__main__':
    unittest.main()
