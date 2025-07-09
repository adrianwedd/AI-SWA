from typing import List, Optional
from .task import Task
from .config import load_config
import logging

logger = logging.getLogger(__name__)


class Planner:
    """Plan task execution order while tracking a cost budget."""

    def __init__(self, budget: int | None = None, warning_threshold: float | None = None) -> None:
        cfg = load_config()
        planner_cfg = cfg.get("planner", {})
        self.budget = budget if budget is not None else planner_cfg.get("budget", 0)
        self.warning_threshold = (
            warning_threshold if warning_threshold is not None else planner_cfg.get("warning_threshold", 0.8)
        )
        self.cost_used = 0
        self._warned = False

    def plan(self, tasks: List[Task]) -> Optional[Task]:
        """Determine the next task to execute.

        Tasks with higher priority are selected first. Tasks with dependencies
        are only considered if all their dependencies are marked as ``done``.

        Args:
            tasks: Arbitrary list of :class:`Task` objects.

        Returns:
            The next :class:`Task` to execute or ``None`` if no task is ready.
        """
        if self.budget and self.cost_used >= self.budget:
            logger.warning("Budget exhausted; no further tasks will be planned")
            return None

        self._validate_unique_ids(tasks)
        pending_tasks = self._get_pending_tasks(tasks)
        if not pending_tasks:
            return None

        ready_tasks = [t for t in pending_tasks if self._dependencies_met(t, tasks)]
        if not ready_tasks:
            return None

        selected = self._select_highest_priority(ready_tasks)
        self.cost_used += 1
        if (
            self.budget
            and not self._warned
            and self.cost_used >= self.budget * self.warning_threshold
            and self.cost_used < self.budget
        ):
            logger.warning("Planner budget at %d%%", int(100 * self.cost_used / self.budget))
            self._warned = True
        return selected

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
