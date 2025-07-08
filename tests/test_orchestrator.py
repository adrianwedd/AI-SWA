import unittest
from dataclasses import asdict
from unittest.mock import Mock, MagicMock, call, patch
import yaml
from pathlib import Path
import tempfile
from core.task import Task

# Need to import the actual classes to be instantiated or mocked if type hints are used by Orchestrator
from core.planner import Planner
from core.executor import Executor
from core.reflector import Reflector
from core.memory import Memory
from core.self_auditor import SelfAuditor
from core.orchestrator import Orchestrator


class TestOrchestrator(unittest.TestCase):

    def setUp(self):
        self.mock_planner = MagicMock(spec=Planner)
        self.mock_executor = MagicMock(spec=Executor)
        self.mock_reflector = MagicMock(spec=Reflector)
        self.mock_memory = MagicMock(spec=Memory)
        self.mock_auditor = MagicMock(spec=SelfAuditor)
        self.mock_auditor.audit.return_value = []

        self.orchestrator = Orchestrator(
            planner=self.mock_planner,
            executor=self.mock_executor,
            reflector=self.mock_reflector,
            memory=self.mock_memory,
            auditor=self.mock_auditor
        )

    def test_init_stores_dependencies(self):
        self.assertIs(self.orchestrator.planner, self.mock_planner)
        self.assertIs(self.orchestrator.executor, self.mock_executor)
        self.assertIs(self.orchestrator.reflector, self.mock_reflector)
        self.assertIs(self.orchestrator.memory, self.mock_memory)
        self.assertIs(self.orchestrator.auditor, self.mock_auditor)

    def test_run_loop_full_cycle_one_task(self):
        tasks_file = "test_tasks.yml"
        initial_tasks = [Task(id="t0", description="", component="test", dependencies=[], priority=1, status="pending")]  # Tasks loaded from memory
        reflected_tasks = [
            Task(id="t0", description="", component="test", dependencies=[], priority=1, status="pending"),
            Task(id="t_new", description="New task from reflector", component="test", dependencies=[], priority=1, status="pending")
        ]  # Tasks after reflector ran

        task1_planned = Task(id="t1", description="Task 1", component="test", dependencies=[], priority=1, status="pending")

        self.mock_memory.load_tasks.return_value = initial_tasks
        self.mock_reflector.run_cycle.return_value = reflected_tasks

        # Planner will return task1 first, then None to terminate
        self.mock_planner.plan.side_effect = [task1_planned, None]

        with patch('builtins.print') as mock_print: # Suppress print output during test
            self.orchestrator.run(tasks_file)

        # Verify initial load
        self.mock_memory.load_tasks.assert_called_once_with(tasks_file)

        # Verify reflector call
        self.mock_reflector.run_cycle.assert_called_once_with([asdict(t) for t in initial_tasks])
        self.mock_memory.save_tasks.assert_any_call(reflected_tasks, tasks_file)  # First save after reflection

        # Verify planner calls (called twice: once for task1, once for None)
        self.mock_planner.plan.assert_has_calls([call(reflected_tasks), call(reflected_tasks)])

        # Verify task1 status updates and save calls
        # 1. After reflection
        # 2. Status to "in_progress"
        # 3. Status to "done"
        self.assertEqual(self.mock_memory.save_tasks.call_count, 3)

        # Check specific calls for task1_planned
        # Note: reflected_tasks list is modified in place by the orchestrator for status.
        # So task1_planned which is part of that list (or conceptually represents an item in it)
        # will have its status changed.

        # Call after reflection (already asserted by assert_any_call)
        # self.mock_memory.save_tasks.assert_any_call(reflected_tasks, tasks_file)

        # After marking "in_progress"
        self.assertEqual(task1_planned.status, "done") # Status should be 'done' by the end of its processing
                                                       # The test checks final state.
                                                       # To check intermediate, would need more complex mocking or state capture.

        # Check that save_tasks was called with the tasks list when task1 was in_progress
        # This requires inspecting the actual arguments to save_tasks.
        # The third argument to assert_any_call is the index of the call if there are multiple.
        # We expect save_tasks to be called with task1 status as "in_progress"
        # And then again with task1 status as "done"

        # Create expected task states for save calls
        # State after reflection (this is reflected_tasks)
        # State with task1_planned as "in_progress"
        tasks_after_reflection = reflected_tasks # This is the list instance used

        # The orchestrator modifies the task object directly.
        # So when save_tasks is called, task1_planned.status would have been updated.

        # Executor call
        self.mock_executor.execute.assert_called_once_with(task1_planned)

        # Final status of task1 should be "done"
        self.assertEqual(task1_planned.status, "done")

        # Check the sequence of save_tasks more carefully for status changes
        # Call 1: After reflector.run_cycle
        #   reflected_tasks might have new tasks. Task1 is not yet processed.
        # Call 2: Task1 status -> "in_progress"
        # Call 3: Task1 status -> "done"

        args_list = self.mock_memory.save_tasks.call_args_list
        self.assertEqual(len(args_list), 3)

        # Call 1: after reflection
        self.assertEqual(args_list[0], call(reflected_tasks, tasks_file))

        # For calls 2 and 3, the 'tasks' list (which is 'reflected_tasks') is modified in place.
        # So, task1_planned (which is an item from that list conceptually) will have its status changed.
        # When testing save_tasks for "in_progress", we'd expect the *object* task1_planned
        # to have status "in_progress" *at the time of that specific call*.
        # This is hard to assert directly with simple mock call_args_list if the object is mutated.
        # However, we know execute is called between "in_progress" and "done" saves.

        # A practical way to check:
        # - save_tasks was called 3 times (already did)
        # - execute was called once with task1_planned (already did)
        # - The task object passed to execute should have status "in_progress" at that point.
        #   This requires execute to be called *before* status changes to "done".
        #   The orchestrator logic is: status="in_progress" -> save -> execute -> status="done" -> save.

        # To verify the status at the time of execute:
        # We can change the mock_executor.execute to a side_effect function that asserts status
        def execute_side_effect(task_arg):
            self.assertEqual(task_arg.status, "in_progress", "Task status should be 'in_progress' when execute is called")
        self.mock_executor.execute.side_effect = execute_side_effect

        # Rerun with the side effect (need to reset mocks that track calls)
        self.mock_memory.reset_mock()
        self.mock_reflector.reset_mock()
        self.mock_planner.reset_mock()
        self.mock_executor.reset_mock() # Resetting this mock means we need to re-assign side_effect

        self.mock_executor.execute.side_effect = execute_side_effect # Re-assign after reset
        self.mock_memory.load_tasks.return_value = initial_tasks
        self.mock_reflector.run_cycle.return_value = reflected_tasks
        task1_planned.status = "pending" # Reset status before rerun
        self.mock_planner.plan.side_effect = [task1_planned, None]

        with patch('builtins.print') as mock_print:
             self.orchestrator.run(tasks_file)

        # Now the execute_side_effect assertion would have run.
        # And we can re-verify other calls.
        self.mock_memory.load_tasks.assert_called_once_with(tasks_file)
        self.mock_reflector.run_cycle.assert_called_once_with([asdict(t) for t in initial_tasks])
        self.mock_executor.execute.assert_called_once_with(task1_planned)
        self.assertEqual(task1_planned.status, "done") # Final status
        self.assertEqual(self.mock_memory.save_tasks.call_count, 3)

    def test_auditor_generated_tasks_are_appended(self):
        tasks_file = "audit.yml"
        base_task = Task(id=1, description="base", component="core", dependencies=[], priority=1, status="pending")

        self.mock_memory.load_tasks.return_value = [base_task]
        self.mock_reflector.run_cycle.return_value = [base_task]
        self.mock_planner.plan.side_effect = [base_task, None]

        audit_task = {
            "id": 2,
            "description": "Refactor foo.py",
            "component": "refactor",
            "dependencies": [],
            "priority": 2,
            "status": "pending",
        }
        self.mock_auditor.audit.return_value = [audit_task]

        with patch('builtins.print'):
            self.orchestrator.run(tasks_file)

        self.mock_auditor.audit.assert_called()
        # After audit there should be an extra save with the new task appended
        args = self.mock_memory.save_tasks.call_args_list[-1].args[0]
        self.assertEqual(len(args), 2)
        self.assertEqual(args[-1].description, "Refactor foo.py")


    def test_run_loop_no_tasks_from_memory_and_no_new_tasks_from_reflector(self):
        tasks_file = "empty_tasks.yml"
        self.mock_memory.load_tasks.return_value = []  # No tasks loaded
        self.mock_reflector.run_cycle.return_value = [] # No new tasks from reflector
        self.mock_planner.plan.return_value = None # Planner finds nothing to do

        self.orchestrator.logger = MagicMock()
        with patch('builtins.print'):
            self.orchestrator.run(tasks_file)

        self.mock_memory.load_tasks.assert_called_once_with(tasks_file)
        self.mock_reflector.run_cycle.assert_called_once_with([])
        self.mock_memory.save_tasks.assert_called_once_with([], tasks_file) # Saved empty list after reflection
        self.mock_planner.plan.assert_called_once_with([]) # Called with empty list
        self.mock_executor.execute.assert_not_called() # No task execution

    def test_run_loop_terminates_when_planner_returns_none(self):
        tasks_file = "tasks.yml"
        initial_tasks = [Task(id="t1", description="", component="test", dependencies=[], priority=1, status="pending")]
        self.mock_memory.load_tasks.return_value = initial_tasks
        self.mock_reflector.run_cycle.return_value = initial_tasks # Reflector adds no new tasks
        self.mock_planner.plan.return_value = None # Planner immediately says nothing to do

        self.orchestrator.logger = MagicMock()
        with patch('builtins.print'):
            self.orchestrator.run(tasks_file)

        self.mock_memory.load_tasks.assert_called_once_with(tasks_file)
        self.mock_reflector.run_cycle.assert_called_once_with([asdict(t) for t in initial_tasks])
        self.mock_memory.save_tasks.assert_called_once_with(initial_tasks, tasks_file) # After reflection
        self.mock_planner.plan.assert_called_once_with(initial_tasks)
        self.mock_executor.execute.assert_not_called()

    def test_run_handles_load_tasks_returning_none(self):
        tasks_file = "non_existent_tasks.yml"
        self.mock_memory.load_tasks.return_value = None # Simulate file not found / load error
        self.mock_reflector.run_cycle.return_value = [] # Reflector works with empty list
        self.mock_planner.plan.return_value = None

        with patch('builtins.print') as mock_print:
            self.orchestrator.run(tasks_file)

        self.mock_memory.load_tasks.assert_called_once_with(tasks_file)
        self.mock_reflector.run_cycle.assert_called_once_with([]) # Called with empty list
        self.mock_memory.save_tasks.assert_called_once_with([], tasks_file)
        self.mock_planner.plan.assert_called_once_with([])
        self.mock_executor.execute.assert_not_called()

    def test_run_task_missing_status_attribute(self):
        # Test robustness if a task somehow doesn't have 'status'
        tasks_file = "tasks_no_status.yml"
        task_no_status = Task(id="t_no_stat", description="Test", component="test", dependencies=[], priority=1, status="pending")
        if hasattr(task_no_status, 'status'): # Ensure it's not there
            delattr(task_no_status, 'status')

        initial_tasks = [task_no_status]

        self.mock_memory.load_tasks.return_value = initial_tasks
        self.mock_reflector.run_cycle.return_value = initial_tasks
        self.mock_planner.plan.side_effect = [task_no_status, None] # Planner returns this malformed task

        with patch('builtins.print') as mock_print:
            self.orchestrator.run(tasks_file)

        # Orchestrator should attempt to run it, print warnings, but not crash.
        self.mock_executor.execute.assert_called_once_with(task_no_status)
        # Check for warning prints (optional, but good for robustness check)
        # Example: mock_print.assert_any_call(Your warning message for missing status)

        # The number of save_tasks calls might be different if status updates fail silently
        # or are skipped. Original logic has 3 saves for one task.
        # 1. After reflection
        # 2/3. Skipped if hasattr(next_task, 'status') is false.
        # Let's check the implementation of orchestrator: it uses hasattr.
        # So, if no 'status', it prints a warning and doesn't try to set it.
        # Thus, only one save (after reflection) should occur.
        self.assertEqual(self.mock_memory.save_tasks.call_count, 1)
        self.mock_memory.save_tasks.assert_called_once_with(initial_tasks, tasks_file)

    def test_run_task_missing_id_attribute(self):
        tasks_file = "tasks_no_id.yml"
        task_no_id = Task(id="x", description="Test", component="core", dependencies=[], priority=1, status="pending")
        if hasattr(task_no_id, 'id'):
            delattr(task_no_id, 'id')

        self.mock_memory.load_tasks.return_value = [task_no_id]
        self.mock_reflector.run_cycle.return_value = [task_no_id]
        self.mock_planner.plan.side_effect = [task_no_id, None]

        self.orchestrator.logger = MagicMock()
        with patch("builtins.print"):
            self.orchestrator.run(tasks_file)

        self.mock_executor.execute.assert_called_once_with(task_no_id)
        self.assertEqual(task_no_id.status, 'done')
        self.assertEqual(self.mock_memory.save_tasks.call_count, 3)
        self.orchestrator.logger.info.assert_any_call("Orchestrator: Task '%s' selected for execution.", "N/A")
        self.orchestrator.logger.info.assert_any_call("Orchestrator: Executing task '%s'.", "N/A")

    def test_reflector_returns_invalid_data_raises_error(self):
        tasks_file = "tasks_invalid.yml"
        self.mock_memory.load_tasks.return_value = []
        self.mock_reflector.run_cycle.return_value = ["bad"]
        self.mock_planner.plan.return_value = None

        with patch('builtins.print'):
            with self.assertRaises(Exception):
                self.orchestrator.run(tasks_file)

        self.mock_memory.save_tasks.assert_not_called()

    def test_run_updates_tasks_file_after_reflection(self):
        tmp_path = Path(tempfile.mkdtemp())
        tasks_file = tmp_path / "tasks.yml"
        state_file = tmp_path / "state.json"
        memory = Memory(state_file)

        base_task = Task(id=1, description="base", component="core", dependencies=[], priority=1, status="pending")
        memory.save_tasks([base_task], tasks_file)

        class DummyPlanner:
            def __init__(self):
                self.calls = 0

            def plan(self, tasks):
                if self.calls == 0:
                    self.calls += 1
                    return tasks[0]
                return None

        class DummyExecutor:
            def execute(self, task):
                pass

        class DummyReflector:
            def __init__(self):
                self.called = False

            def run_cycle(self, tasks):
                self.called = True
                tasks.append({
                    "id": 2,
                    "description": "reflector task",
                    "component": "core",
                    "dependencies": [],
                    "priority": 1,
                    "status": "pending",
                })
                return tasks

        auditor = MagicMock(spec=SelfAuditor)
        auditor.audit.return_value = []

        orch = Orchestrator(DummyPlanner(), DummyExecutor(), DummyReflector(), memory, auditor)

        with patch('builtins.print'):
            orch.run(str(tasks_file))

        data = yaml.safe_load(tasks_file.read_text())
        assert len(data) == 2
        assert data[0]['status'] == 'done'
        assert data[1]['description'] == 'reflector task'

    def test_execute_failure_logs_and_continues(self):
        task = Task(id="fail", description="", component="core", dependencies=[], priority=1, status="pending")
        self.mock_memory.load_tasks.return_value = [task]
        self.mock_reflector.run_cycle.return_value = [task]
        self.mock_planner.plan.side_effect = [task, None]
        self.mock_executor.execute.side_effect = RuntimeError("boom")
        self.orchestrator.logger = MagicMock()

        with patch('builtins.print'):
            self.orchestrator.run("tasks.yml")

        self.mock_executor.execute.assert_called_once_with(task)
        self.orchestrator.logger.exception.assert_called_once()
        self.assertEqual(task.status, "pending")
        self.assertEqual(self.mock_memory.save_tasks.call_count, 3)

    def test_reflect_failure_logs_and_skips_execution(self):
        task = Task(id="t1", description="", component="core", dependencies=[], priority=1, status="pending")
        self.mock_memory.load_tasks.return_value = [task]
        self.mock_reflector.run_cycle.side_effect = ValueError("oops")
        self.mock_planner.plan.return_value = None
        self.orchestrator.logger = MagicMock()

        with patch('builtins.print'):
            self.orchestrator.run("tasks.yml")

        self.orchestrator.logger.exception.assert_called_once()
        self.mock_executor.execute.assert_not_called()
        self.mock_memory.save_tasks.assert_not_called()

    def test_execute_unexpected_error_propagates(self):
        task = Task(id="boom", description="", component="core", dependencies=[], priority=1, status="pending")
        self.mock_memory.load_tasks.return_value = [task]
        self.mock_reflector.run_cycle.return_value = [task]
        self.mock_planner.plan.side_effect = [task, None]
        self.mock_executor.execute.side_effect = KeyError("fail")

        with patch('builtins.print'):
            with self.assertRaises(KeyError):
                self.orchestrator.run("tasks.yml")
        self.assertEqual(task.status, "in_progress")

    def test_reflect_unexpected_error_propagates(self):
        self.mock_memory.load_tasks.return_value = []
        self.mock_reflector.run_cycle.side_effect = KeyError("bad")
        self.orchestrator.logger = MagicMock()

        with patch('builtins.print'):
            with self.assertRaises(KeyError):
                self.orchestrator.run("tasks.yml")


if __name__ == '__main__':
    unittest.main()
