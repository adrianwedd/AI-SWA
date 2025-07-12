"""Map Vision Engine goals to executable tasks."""

from dataclasses import dataclass
from typing import List

from .task import Task


@dataclass
class Epic:
    """Representation of a high-level goal from the Vision Engine."""

    id: int
    title: str
    steps: List[str]


class IntentMapper:
    """Decompose epics into concrete tasks with dependencies."""

    def __init__(self, default_priority: int = 1) -> None:
        self.default_priority = default_priority

    def decompose_epic(self, epic: Epic, start_id: int = 1) -> List[Task]:
        """Return tasks for ``epic`` starting at ``start_id``.

        Tasks are ordered sequentially so that each depends on the previous one.
        """
        tasks: List[Task] = []
        prev_id = None
        tid = start_id
        for step in epic.steps:
            tasks.append(
                Task(
                    id=tid,
                    description=step,
                    dependencies=[prev_id] if prev_id is not None else [],
                    priority=self.default_priority,
                    status="pending",
                    epic=epic.title,
                )
            )
            prev_id = tid
            tid += 1
        return tasks

    def map_goals(self, epics: List[Epic], start_id: int = 1) -> List[Task]:
        """Convert a list of epics into an aggregated task list."""
        tasks: List[Task] = []
        tid = start_id
        for epic in epics:
            epic_tasks = self.decompose_epic(epic, start_id=tid)
            tasks.extend(epic_tasks)
            tid += len(epic_tasks)
        return tasks
