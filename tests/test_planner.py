import unittest
from core.planner import Planner
from core.task import Task

class TestPlanner(unittest.TestCase):

    def setUp(self):
        self.planner = Planner()

    def _create_task(self, id, priority, status, dependencies=None, description="A task"):
        """Helper to create task-like objects."""
        if dependencies is None:
            dependencies = []
        return Task(id=id, priority=priority, status=status, dependencies=dependencies, description=description, component="test")

    def test_empty_tasks_list(self):
        self.assertIsNone(self.planner.plan([]), "Should return None for empty task list")

    def test_no_actionable_tasks_all_done(self):
        tasks = [self._create_task("t1", 10, "done")]
        self.assertIsNone(self.planner.plan(tasks), "Should return None if all tasks are done")

    def test_no_actionable_tasks_all_inprogress(self):
        tasks = [self._create_task("t1", 10, "in_progress")]
        self.assertIsNone(self.planner.plan(tasks), "Should return None if all tasks are in_progress")

    def test_priority_selection(self):
        task1 = self._create_task("t1", 10, "pending")
        task2 = self._create_task("t2", 20, "pending")
        task3 = self._create_task("t3", 5, "pending")
        selected_task = self.planner.plan([task1, task2, task3])
        self.assertEqual(selected_task.id, "t2", "Should select task with highest priority")

    def test_select_only_pending_tasks(self):
        task1 = self._create_task("t1", 10, "done")
        task2 = self._create_task("t2", 20, "pending")
        task3 = self._create_task("t3", 5, "other_status")
        selected_task = self.planner.plan([task1, task2, task3])
        self.assertIsNotNone(selected_task)
        self.assertEqual(selected_task.id, "t2", "Should only consider pending tasks")

    def test_dependency_unmet_because_dependency_is_pending(self):
        dep_task = self._create_task("dep1", 5, "pending", []) # Dependency is 'pending', not 'done'
        main_task = self._create_task("main1", 10, "pending", ["dep1"])
        tasks = [dep_task, main_task]
        selected_task = self.planner.plan(tasks)
        # main_task is blocked because dep1 is not "done". So, dep1 (priority 5) should be selected.
        self.assertEqual(selected_task.id, "dep1", "Should select the pending dependency, not the blocked task")

    def test_dependency_unmet_because_dependency_is_in_progress(self):
        dep_task = self._create_task("dep1", 5, "in_progress", []) # Dependency is 'in_progress', not 'done'
        main_task = self._create_task("main1", 10, "pending", ["dep1"])
        # other_task is a lower priority pending task that is not blocked
        other_task = self._create_task("other", 1, "pending", [])
        tasks = [dep_task, main_task, other_task]
        selected_task = self.planner.plan(tasks)
        # main_task is blocked. dep_task is not pending. So other_task should be chosen.
        self.assertEqual(selected_task.id, "other", "Should select 'other' task as main_task is blocked and dep_task is not pending")


    def test_dependency_met(self):
        dep_task = self._create_task("dep1", 5, "done", [])
        main_task = self._create_task("main1", 10, "pending", ["dep1"])
        other_task = self._create_task("other", 1, "pending", []) # Lower priority, no deps
        tasks = [dep_task, main_task, other_task]
        selected_task = self.planner.plan(tasks)
        self.assertEqual(selected_task.id, "main1", "Should select task when dependency is met")

    def test_dependency_missing_in_list(self):
        main_task = self._create_task("main1", 10, "pending", ["dep_missing"])
        other_task_pending = self._create_task("other", 5, "pending")
        tasks = [main_task, other_task_pending]
        selected_task = self.planner.plan(tasks)
        self.assertEqual(selected_task.id, "other", "Should not select task if dependency is missing from list, select other pending task")

    def test_complex_scenario_priority_and_dependencies(self):
        t_done1 = self._create_task("td1", 1, "done") # Done
        t_pending_blocked_missing_dep = self._create_task("tpb_missing", 20, "pending", ["td_missing"]) # Blocked
        t_pending_dep_on_done1 = self._create_task("tpd1", 10, "pending", ["td1"]) # Ready, Prio 10
        t_pending_nodep_low_priority = self._create_task("tpnlp", 5, "pending")    # Ready, Prio 5
        t_pending_dep_on_pending = self._create_task("tpdp", 15, "pending", ["tpnlp"]) # Blocked by tpnlp (which is pending)

        tasks = [t_done1, t_pending_blocked_missing_dep, t_pending_dep_on_done1, t_pending_nodep_low_priority, t_pending_dep_on_pending]

        # Expected: tpd1 (priority 10) is chosen as its dep td1 is done.
        # tpb_missing is blocked (missing dep).
        # tpnlp is ready (prio 5).
        # tpdp is blocked by tpnlp (prio 15 but dep not done).
        selected_task = self.planner.plan(tasks)
        self.assertEqual(selected_task.id, "tpd1", "Should select tpd1 (priority 10, deps met)")

        # Simulate tpd1 being completed
        t_pending_dep_on_done1.status = "done"

        # Now, tpnlp (prio 5) should be chosen next. tpdp is still blocked by tpnlp.
        selected_task_2 = self.planner.plan(tasks)
        self.assertEqual(selected_task_2.id, "tpnlp", "Should select tpnlp (priority 5) next")

        # Simulate tpnlp being completed
        t_pending_nodep_low_priority.status = "done"

        # Now, tpdp (priority 15) should be chosen as its dependency tpnlp is done.
        selected_task_3 = self.planner.plan(tasks)
        self.assertEqual(selected_task_3.id, "tpdp", "Should select tpdp (priority 15, deps now met)")

        # Simulate tpdp being completed
        t_pending_dep_on_pending.status = "done"

        # Now, only t_pending_blocked_missing_dep is left, but it's blocked. So, None.
        selected_task_4 = self.planner.plan(tasks)
        self.assertIsNone(selected_task_4, "Should be None as only a blocked task remains")


    def test_no_actionable_all_blocked_by_unmet_dependency(self):
        task_a = self._create_task("task_a", 10, "pending", ["task_b"])
        task_b = self._create_task("task_b", 5, "in_progress", []) # task_b is not 'done'
        tasks_blocked = [task_a, task_b]
        self.assertIsNone(self.planner.plan(tasks_blocked), "Should return None if all pending tasks are blocked by unmet deps")

    def test_no_actionable_all_blocked_by_missing_dependency(self):
        task_a = self._create_task("task_a", 10, "pending", ["task_missing"])
        tasks_blocked = [task_a]
        self.assertIsNone(self.planner.plan(tasks_blocked), "Should return None if all pending tasks are blocked by missing deps")

    def test_task_with_no_dependencies_attribute(self):
        task_no_deps_attr = self._create_task("t_no_dep_attr", 10, "pending")
        if hasattr(task_no_deps_attr, 'dependencies'):
            delattr(task_no_deps_attr, 'dependencies')

        selected_task = self.planner.plan([task_no_deps_attr])
        self.assertIsNotNone(selected_task)
        self.assertEqual(selected_task.id, "t_no_dep_attr", "Should select task if 'dependencies' attribute is missing")

    def test_task_with_empty_dependencies_list(self):
        task_empty_deps = self._create_task("t_empty_deps", 10, "pending", [])
        selected_task = self.planner.plan([task_empty_deps])
        self.assertEqual(selected_task.id, "t_empty_deps", "Should select task with empty dependencies list")

    def test_task_object_without_priority_attribute_defaults_to_zero(self):
        task_no_priority = self._create_task("t_no_prio", 0, "pending", [])
        if hasattr(task_no_priority, 'priority'):
            delattr(task_no_priority, 'priority')
        task_with_priority_one = self._create_task("t_with_prio", 1, "pending")

        # Test order 1: no_priority first in list
        selected1 = self.planner.plan([task_no_priority, task_with_priority_one])
        self.assertEqual(selected1.id, "t_with_prio", "Task with priority 1 should be chosen over default 0")

        # Test order 2: with_priority first in list
        selected2 = self.planner.plan([task_with_priority_one, task_no_priority])
        self.assertEqual(selected2.id, "t_with_prio", "Task with priority 1 should be chosen over default 0")

    def test_all_tasks_pending_no_dependencies_highest_priority_selected(self):
        tasks = [
            self._create_task("task_low", 1, "pending"),
            self._create_task("task_high", 10, "pending"),
            self._create_task("task_mid", 5, "pending"),
        ]
        selected = self.planner.plan(tasks)
        self.assertEqual(selected.id, "task_high")

    def test_mix_of_statuses_dependencies_priority(self):
        tasks = [
            self._create_task("done_dep", 1, "done"),
            self._create_task("pending_dep_on_done", 10, "pending", ["done_dep"]), # Should be selected
            self._create_task("pending_low_prio", 5, "pending"),
            self._create_task("in_progress_task", 100, "in_progress"), # Not pending
            self._create_task("pending_blocked", 20, "pending", ["non_existent_dep"]) # Blocked
        ]
        selected = self.planner.plan(tasks)
        self.assertEqual(selected.id, "pending_dep_on_done")

    def test_duplicate_task_ids_raise_error(self):
        tasks = [
            self._create_task("dup", 1, "pending"),
            self._create_task("dup", 2, "pending"),
        ]
        with self.assertRaises(ValueError):
            self.planner.plan(tasks)

    def test_warning_emitted_for_missing_dependency(self):
        task = self._create_task("main", 5, "pending", ["missing"])
        with self.assertLogs("core.planner", level="WARNING") as cm:
            self.planner.plan([task])
        self.assertTrue(any("missing" in msg for msg in cm.output))

    def test_get_pending_tasks_helper(self):
        tasks = [
            self._create_task("a", 1, "done"),
            self._create_task("b", 2, "pending"),
            self._create_task("c", 3, "in_progress"),
        ]
        pending = self.planner._get_pending_tasks(tasks)
        self.assertEqual(len(pending), 1)
        self.assertEqual(pending[0].id, "b")

    def test_dependencies_met_helper(self):
        dep_done = self._create_task("dep", 1, "done")
        main = self._create_task("main", 1, "pending", ["dep"])
        self.assertTrue(self.planner._dependencies_met(main, [dep_done, main]))

        dep_pending = self._create_task("dep_p", 1, "pending")
        blocked = self._create_task("blocked", 1, "pending", ["dep_p"])
        self.assertFalse(self.planner._dependencies_met(blocked, [blocked, dep_pending]))


if __name__ == '__main__':
    unittest.main()
