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
        """
        Determines the next task to execute based on priority and dependencies.

        Tasks with higher priority are selected first.
        Tasks with dependencies are only selected if all their dependent tasks
        have a status of "done".

        Args:
            tasks: A list of :class:`Task` objects ordered arbitrarily.

        Returns:
            The next :class:`Task` object to execute, or ``None`` if no tasks can be
            executed (e.g., all tasks are done, or pending tasks have unmet
            dependencies).
        """
        seen_ids = set()
        for task in tasks:
            task_id = getattr(task, 'id', None)
            if task_id in seen_ids:
                raise ValueError(f"Duplicate task id {task_id} detected")
            if task_id is not None:
                seen_ids.add(task_id)

        # Filter tasks that are "pending"
        pending_tasks = [task for task in tasks if hasattr(task, 'status') and task.status == "pending"]

        if not pending_tasks:
            return None

        ready_tasks = []
        for task in pending_tasks:
            if not hasattr(task, 'dependencies') or not task.dependencies:
                # Task has no dependencies
                ready_tasks.append(task)
                continue

            dependencies_met = True
            for dep_id in task.dependencies:
                # Find the dependent task in the original list
                dependent_task = next(
                    (t for t in tasks if hasattr(t, 'id') and t.id == dep_id),
                    None,
                )

                if not dependent_task:
                    logger.warning(
                        "Task %s skipped: dependency %s not found",
                        getattr(task, "id", "<unknown>"),
                        dep_id,
                    )
                    dependencies_met = False
                    break

                # If dependency task exists but is not "done", it's not met
                if not hasattr(dependent_task, 'status') or dependent_task.status != "done":
                    dependencies_met = False
                    break

            if dependencies_met:
                ready_tasks.append(task)

        if not ready_tasks:
            return None

        # Sort ready tasks by priority (highest first)
        # Assumes tasks in ready_tasks have 'priority' attribute
        ready_tasks.sort(key=lambda t: getattr(t, 'priority', 0), reverse=True)

        return ready_tasks[0]
