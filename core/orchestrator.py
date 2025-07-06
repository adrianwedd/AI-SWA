"""High-level coordinator for planner, executor and auditor."""

from typing import List
from opentelemetry import metrics, trace
import logging

from .task import Task



class Orchestrator:
    """Coordinate the self-improving loop of planning and execution."""

    def __init__(self, planner, executor, reflector, memory, auditor):
        """Store dependencies for later use."""

        self.planner = planner
        self.executor = executor
        self.reflector = reflector
        self.memory = memory
        self.auditor = auditor
        self.logger = logging.getLogger(__name__)
        meter = metrics.get_meter_provider().get_meter(__name__)
        self._runs = meter.create_counter(
            "orchestrator_runs_total", description="Number of orchestrator loops"
        )
        self._tracer = trace.get_tracer(__name__)

    # ------------------------------------------------------------------
    def _task_to_dict(self, task: Task) -> dict:
        return {f: getattr(task, f) for f in Task.__dataclass_fields__ if hasattr(task, f)}

    # ------------------------------------------------------------------
    def _load_tasks(self, tasks_file: str) -> List[Task]:
        tasks = self.memory.load_tasks(tasks_file)
        return tasks or []

    # ------------------------------------------------------------------
    def _reflect(self, tasks: List[Task], tasks_file: str) -> List[Task]:
        try:
            reflected = self.reflector.run_cycle([self._task_to_dict(t) for t in tasks])
        except Exception as exc:  # pragma: no cover - defensive
            self.logger.error("Reflection failed: %s", exc)
            return tasks
        if reflected is None:
            return tasks
        if reflected and isinstance(reflected[0], Task):
            tasks = reflected
        else:
            fields = set(Task.__dataclass_fields__.keys())
            tasks = [Task(**{k: v for k, v in item.items() if k in fields}) for item in reflected]
        self.memory.save_tasks(tasks, tasks_file)
        return tasks

    # ------------------------------------------------------------------
    def _execute_task(self, task: Task, tasks: List[Task], tasks_file: str) -> None:
        if hasattr(task, "status"):
            task.status = "in_progress"
            self.memory.save_tasks(tasks, tasks_file)
        else:
            print(f"Warning: Task '{getattr(task, 'id', 'N/A')}' has no 'status' attribute.")

        print(f"Orchestrator: Executing task '{getattr(task, 'id', 'N/A')}'.")
        try:
            self.executor.execute(task)
        except Exception as exc:  # pragma: no cover - executor issues
            self.logger.error("Execution failed for task %s: %s", getattr(task, 'id', 'N/A'), exc)
            if hasattr(task, "status"):
                task.status = "pending"
                self.memory.save_tasks(tasks, tasks_file)
            return

        if hasattr(task, "status"):
            task.status = "done"
            self.memory.save_tasks(tasks, tasks_file)
        else:
            print(
                f"Warning: Task '{getattr(task, 'id', 'N/A')}' has no 'status' attribute to mark as done."
            )

        print(f"Orchestrator: Task '{getattr(task, 'id', 'N/A')}' completed.")

        audit_results = self.auditor.audit([self._task_to_dict(t) for t in tasks])
        if audit_results:
            fields = set(Task.__dataclass_fields__.keys())
            new_tasks = [Task(**{k: v for k, v in item.items() if k in fields}) for item in audit_results]
            tasks.extend(new_tasks)
            self.memory.save_tasks(tasks, tasks_file)

    def run(self, tasks_file: str = "tasks.yml") -> None:
        """Run the orchestration loop."""
        attrs = {"tasks.file": tasks_file}
        with self._tracer.start_as_current_span("orchestrator.run", attributes=attrs):
            tasks: List[Task] = self._load_tasks(tasks_file)
            tasks = self._reflect(tasks, tasks_file)

            while True:
                next_task = self.planner.plan(tasks)
                if next_task is None:
                    print("Orchestrator: No actionable tasks. Halting.")
                    break

                print(f"Orchestrator: Task '{getattr(next_task, 'id', 'N/A')}' selected for execution.")
                self._execute_task(next_task, tasks, tasks_file)
                self._runs.add(1)

            print("Orchestrator: Run finished.")
