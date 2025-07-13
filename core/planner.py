"""Core planning algorithm used by the orchestrator.

The heavy lifting such as dependency evaluation and budget tracking is
implemented in :mod:`core.planner_utils` to keep this module small and
easy to maintain.
"""

from typing import List, Optional
import logging

from .task import Task
from .config import load_config
from .planner_utils import (
    validate_unique_ids,
    get_pending_tasks,
    select_highest_priority,
    filter_ready_tasks,
    is_budget_exhausted,
    should_warn_about_budget,
    increment_cost_and_warn,
    will_exceed_budget,
)

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
        if is_budget_exhausted(self.budget, self.cost_used):
            logger.warning("Budget exhausted; no further tasks will be planned")
            return None

        validate_unique_ids(tasks)
        pending_tasks = get_pending_tasks(tasks)
        if not pending_tasks:
            return None

        ready_tasks = filter_ready_tasks(pending_tasks, tasks)
        if not ready_tasks:
            return None

        selected = select_highest_priority(ready_tasks)
        cost = getattr(selected, "cost", 1)
        if will_exceed_budget(self.budget, self.cost_used, cost):
            logger.warning(
                "Task %s exceeds remaining budget", getattr(selected, "id", "N/A")
            )
            return None
        self.cost_used, self._warned = increment_cost_and_warn(
            self.cost_used,
            self.budget,
            self.warning_threshold,
            self._warned,
            increment=cost,
        )
        return selected

