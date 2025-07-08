from __future__ import annotations

import logging
import subprocess
import shlex
from datetime import datetime
from pathlib import Path
import time

from opentelemetry import metrics, trace


class Executor:
    """Carry out tasks and capture their output."""

    def __init__(self) -> None:
        meter = metrics.get_meter_provider().get_meter(__name__)
        self.logger = logging.getLogger(__name__)
        self._tasks_executed = meter.create_counter(
            "tasks_executed_total", description="Number of executed tasks"
        )
        self._task_duration = meter.create_histogram(
            "task_duration_seconds", description="Task execution duration"
        )
        self._tracer = trace.get_tracer(__name__)

    def execute(self, task: object) -> None:
        """Execute ``task`` and write any command output to ``logs/``.

        If the task defines a ``command`` attribute, it will be executed in a
        subprocess. The combined stdout and stderr are written to a timestamped
        log file under ``logs/``.

        Parameters
        ----------
        task:
            Object representing the task to execute. It may define
            ``description`` and/or ``command`` attributes.
        """

        if hasattr(task, "description"):
            self.logger.info("Executing task: %s", task.description)
        elif hasattr(task, "id"):
            self.logger.info("Executing task ID: %s (No description found)", task.id)
        else:
            self.logger.info("Executing task: (No description or ID found)")

        command = getattr(task, "command", None)
        if not command:
            return

        attrs = {"task.id": getattr(task, "id", "unknown")}
        start_time = time.perf_counter()
        with self._tracer.start_as_current_span("executor.execute", attributes=attrs):
            args = shlex.split(command)
            result = subprocess.run(args, capture_output=True, text=True)
        duration = time.perf_counter() - start_time

        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        log_file = log_dir / f"task-{getattr(task, 'id', 'unknown')}-{timestamp}.log"
        log_file.write_text(result.stdout + result.stderr)

        self._tasks_executed.add(1, attrs)
        self._task_duration.record(duration, attrs)
