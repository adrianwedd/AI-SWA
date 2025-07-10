from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, List


@dataclass
class Scheduler:
    """Very small synchronous scheduler for training loops."""

    tasks: List[Callable[[], None]] = field(default_factory=list)

    def schedule(self, task: Callable[[], None]) -> None:
        """Queue ``task`` for execution."""
        self.tasks.append(task)

    def run(self) -> None:
        """Run all queued tasks in order."""
        for task in list(self.tasks):
            task()
        self.tasks.clear()
