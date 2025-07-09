"""High-level coordinator for planner, executor and auditor."""

from typing import List
from .sentinel import EthicalSentinel
try:
    from opentelemetry import metrics, trace
except Exception:  # pragma: no cover - optional dependency
    metrics = None
    trace = None
import logging
import subprocess

from .log_utils import configure_logging

from .task import Task



class Orchestrator:
    """Coordinate the self-improving loop of planning and execution."""

    def __init__(self, planner, executor, reflector, memory, auditor, sentinel: EthicalSentinel | None = None):
        """Store dependencies for later use."""

        configure_logging()
        self.planner = planner
        self.executor = executor
        self.reflector = reflector
        self.memory = memory
        self.auditor = auditor
        self.sentinel = sentinel
        self.logger = logging.getLogger(__name__)
        if metrics:
            meter = metrics.get_meter_provider().get_meter(__name__)
            self._runs = meter.create_counter(
                "orchestrator_runs_total", description="Number of orchestrator loops"
            )
            self._tasks_executed = meter.create_counter(
                "tasks_executed_total", description="Number of tasks executed successfully"
            )
        else:  # pragma: no cover - telemetry optional
            self._runs = None
            self._tasks_executed = None
        self._tracer = trace.get_tracer(__name__) if trace else None

    # ------------------------------------------------------------------
    def _task_to_dict(self, task: Task) -> dict:
        return {f: getattr(task, f) for f in Task.__dataclass_fields__ if hasattr(task, f)}

    # ------------------------------------------------------------------
    def _load_tasks(self, tasks_file: str) -> List[Task]:
        try:
            tasks = self.memory.load_tasks(tasks_file)
        except Exception as exc:  # pragma: no cover - defensive
            self.logger.exception("Loading tasks failed: %s", exc)
            return []
        return tasks or []

    # ------------------------------------------------------------------
    def _items_to_tasks(self, items: list) -> List[Task]:
        fields = set(Task.__dataclass_fields__.keys())
        return [Task(**{k: v for k, v in item.items() if k in fields}) for item in items]

    # ------------------------------------------------------------------
    def _convert_reflection(self, reflected) -> List[Task]:
        if reflected and isinstance(reflected[0], Task):
            return list(reflected)
        return self._items_to_tasks(reflected)

    # ------------------------------------------------------------------
    def _reflect(self, tasks: List[Task], tasks_file: str) -> List[Task]:
        try:
            reflected = self.reflector.run_cycle([self._task_to_dict(t) for t in tasks])
        except (ValueError, RuntimeError, FileNotFoundError) as exc:
            # Only handle known reflection issues
            self.logger.exception("Reflection failed: %s", exc)
            return tasks
        if reflected is None:
            return tasks
        tasks = self._convert_reflection(reflected)
        self._save_tasks(tasks, tasks_file)
        return tasks

    # ------------------------------------------------------------------
    def _save_tasks(self, tasks: List[Task], tasks_file: str) -> None:
        """Persist tasks to disk."""
        try:
            self.memory.save_tasks(tasks, tasks_file)
        except Exception as exc:  # pragma: no cover - defensive
            self.logger.exception("Saving tasks failed: %s", exc)

    def _set_status(self, task: Task, status: str, tasks: List[Task], tasks_file: str) -> None:
        """Update task status if possible and persist."""
        if hasattr(task, "status"):
            task.status = status
            self._save_tasks(tasks, tasks_file)
        else:
            self.logger.warning(
                "Task '%s' has no 'status' attribute.", getattr(task, "id", "N/A")
            )

    def _is_blocked(self, task: Task) -> bool:
        """Return True if the Ethical Sentinel blocks this task."""
        if self.sentinel and not self.sentinel.allows(getattr(task, "id", "")):
            self.logger.info(
                "Orchestrator: Task '%s' blocked by Ethical Sentinel.",
                getattr(task, "id", "N/A"),
            )
            return True
        return False

    def _audit_and_extend(self, tasks: List[Task], tasks_file: str) -> None:
        try:
            audit_results = self.auditor.audit([self._task_to_dict(t) for t in tasks])
        except Exception as exc:  # pragma: no cover - defensive
            self.logger.exception("Audit failed: %s", exc)
            return
        if not audit_results:
            return
        new_tasks = self._items_to_tasks(audit_results)
        tasks.extend(new_tasks)
        self._save_tasks(tasks, tasks_file)

    def _execute_task(self, task: Task, tasks: List[Task], tasks_file: str) -> None:
        if self._is_blocked(task):
            return

        self._set_status(task, "in_progress", tasks, tasks_file)

        self.logger.info("Orchestrator: Executing task '%s'.", getattr(task, "id", "N/A"))
        try:
            self.executor.execute(task)
        except (RuntimeError, OSError, subprocess.SubprocessError) as exc:
            self.logger.exception("Execution failed for task %s: %s", getattr(task, "id", "N/A"), exc)
            self._set_status(task, "pending", tasks, tasks_file)
            return

        self._set_status(task, "done", tasks, tasks_file)
        self.logger.info("Orchestrator: Task '%s' completed.", getattr(task, "id", "N/A"))
        if self._tasks_executed:
            self._tasks_executed.add(1)
        self._audit_and_extend(tasks, tasks_file)

    def run(self, tasks_file: str = "tasks.yml") -> None:
        """Run the orchestration loop."""
        attrs = {"tasks.file": tasks_file}
        with self._tracer.start_as_current_span("orchestrator.run", attributes=attrs):
            tasks: List[Task] = self._load_tasks(tasks_file)
            tasks = self._reflect(tasks, tasks_file)

            while True:
                next_task = self.planner.plan(tasks)
                if next_task is None:
                    self.logger.info("Orchestrator: No actionable tasks. Halting.")
                    break

                self.logger.info(
                    "Orchestrator: Task '%s' selected for execution.",
                    getattr(next_task, "id", "N/A"),
                )
                self._execute_task(next_task, tasks, tasks_file)
                self._runs.add(1)

            self.logger.info("Orchestrator: Run finished.")
