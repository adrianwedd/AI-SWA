from __future__ import annotations

import logging
import shlex
import subprocess
from datetime import datetime
from pathlib import Path
import time
from contextlib import nullcontext

from .config import load_config
from .tool_runner import ToolRunner

try:
    from opentelemetry import metrics, trace
except Exception:  # pragma: no cover - optional dependency
    metrics = None
    trace = None


class Executor:
    """Carry out tasks and capture their output."""

    def __init__(self, tool_runner: ToolRunner | None = None) -> None:
        self.logger = logging.getLogger(__name__)
        if metrics:
            meter = metrics.get_meter_provider().get_meter(__name__)
            self._tasks_executed = meter.create_counter(
                "tasks_executed_total", description="Number of executed tasks"
            )
            self._task_duration = meter.create_histogram(
                "task_duration_seconds", description="Task execution duration"
            )
        else:  # pragma: no cover - metrics optional
            self._tasks_executed = None
            self._task_duration = None
        self._tracer = trace.get_tracer(__name__) if trace else None
        cfg = load_config()
        sandbox_cfg = cfg.get("sandbox", {})
        if tool_runner is None:
            tool_runner = ToolRunner(
                sandbox_cfg.get("root", "sandbox"),
                sandbox_cfg.get("allowed_commands", []),
            )
        self.tool_runner = tool_runner

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
        span_ctx = (
            self._tracer.start_as_current_span("executor.execute", attributes=attrs)
            if self._tracer
            else nullcontext()
        )
        with span_ctx:
            result = self.tool_runner.run(command)
        duration = time.perf_counter() - start_time

        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        log_file = log_dir / f"task-{getattr(task, 'id', 'unknown')}-{timestamp}.log"
        log_file.write_text(result.stdout + result.stderr)

        if self._tasks_executed:
            self._tasks_executed.add(1, attrs)
        if self._task_duration:
            self._task_duration.record(duration, attrs)
