import logging
from typing import List, Optional

from .task import Task

logger = logging.getLogger(__name__)


def validate_unique_ids(tasks: List[Task]) -> None:
    """Ensure each task id is unique."""
    seen_ids = set()
    for task in tasks:
        task_id = getattr(task, "id", None)
        if task_id in seen_ids:
            raise ValueError(f"Duplicate task id {task_id} detected")
        if task_id is not None:
            seen_ids.add(task_id)


def get_pending_tasks(tasks: List[Task]) -> List[Task]:
    """Return tasks whose status is ``pending``."""
    return [t for t in tasks if getattr(t, "status", None) == "pending"]


def dependencies_met(task: Task, tasks: List[Task]) -> bool:
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


def select_highest_priority(tasks: List[Task]) -> Task:
    """Return the task with the highest priority."""
    tasks.sort(key=lambda t: getattr(t, "priority", 0), reverse=True)
    return tasks[0]


def filter_ready_tasks(pending_tasks: List[Task], all_tasks: List[Task]) -> List[Task]:
    """Return tasks from ``pending_tasks`` whose dependencies are met."""
    return [t for t in pending_tasks if dependencies_met(t, all_tasks)]


def is_budget_exhausted(budget: Optional[int], cost_used: int) -> bool:
    """Return ``True`` if ``budget`` is set and fully consumed."""
    return bool(budget and cost_used >= budget)


def should_warn_about_budget(budget: Optional[int], cost_used: int, warning_threshold: float, warned: bool) -> bool:
    """Return ``True`` if planner should emit a budget warning."""
    return bool(
        budget
        and not warned
        and cost_used >= budget * warning_threshold
        and cost_used < budget
    )
