from typing import List, Optional
from .task import Task
import logging

logger = logging.getLogger(__name__)


class Planner:
    """
    A class that plans the execution order of tasks.
    It prioritizes tasks based on their priority and dependencies.
    """

    def plan(self, tasks: List[Task]) -> Optional[Task]:
        """Determine the next task to execute.

        Tasks with higher priority are selected first. Tasks with dependencies
        are only considered if all their dependencies are marked as ``done``.

        Args:
            tasks: Arbitrary list of :class:`Task` objects.

        Returns:
            The next :class:`Task` to execute or ``None`` if no task is ready.
        """
        self._validate_unique_ids(tasks)
        pending_tasks = self._get_pending_tasks(tasks)
        if not pending_tasks:
            return None

        ready_tasks = [t for t in pending_tasks if self._dependencies_met(t, tasks)]
        if not ready_tasks:
            return None

        return self._select_highest_priority(ready_tasks)

    def _validate_unique_ids(self, tasks: List[Task]) -> None:
        """Ensure each task id is unique."""
        seen_ids = set()
        for task in tasks:
            task_id = getattr(task, "id", None)
            if task_id in seen_ids:
                raise ValueError(f"Duplicate task id {task_id} detected")
            if task_id is not None:
                seen_ids.add(task_id)

    def _get_pending_tasks(self, tasks: List[Task]) -> List[Task]:
        """Return tasks whose status is ``pending``."""
        return [t for t in tasks if getattr(t, "status", None) == "pending"]

    def _dependencies_met(self, task: Task, tasks: List[Task]) -> bool:
        """Check whether ``task`` has all dependencies completed."""
        if not getattr(task, "dependencies", []):
            return True

        for dep_id in task.dependencies:
            dependent_task = next(
                (t for t in tasks if getattr(t, "id", None) == dep_id),
                None,
            )
            if not dependent_task:
                logger.warning(
                    "Task %s skipped: dependency %s not found",
                    getattr(task, "id", "<unknown>"),
                    dep_id,
                )
                return False
            if getattr(dependent_task, "status", None) != "done":
                return False
        return True

    def _select_highest_priority(self, tasks: List[Task]) -> Task:
        """Return the task with the highest priority."""
        tasks.sort(key=lambda t: getattr(t, "priority", 0), reverse=True)
        return tasks[0]
