"""Command line interface for AI-SWA orchestration."""

import argparse
from pathlib import Path
import sys
import os
import signal
import subprocess

from .orchestrator import Orchestrator
from .memory import Memory
from .planner import Planner
from .executor import Executor
from .reflector import Reflector
from .self_auditor import SelfAuditor
from .telemetry import setup_telemetry
from .log_utils import configure_logging


def build_parser() -> argparse.ArgumentParser:
    """Create and return the command line parser."""
    parser = argparse.ArgumentParser(description="AI-SWE orchestration CLI")
    parser.add_argument(
        "--memory",
        default="state.json",
        help="Path to persistent state file",
    )

    subparsers = parser.add_subparsers(dest="command")
    run = subparsers.add_parser("run", help="Run orchestrator in foreground")
    run.add_argument(
        "--memory",
        default="state.json",
        help="Path to persistent state file",
    )

    start = subparsers.add_parser("start", help="Start orchestrator in background")
    start.add_argument(
        "--pid-file",
        default="orchestrator.pid",
        help="File to store orchestrator PID",
    )
    start.add_argument(
        "--memory",
        default="state.json",
        help="Path to persistent state file",
    )

    stop = subparsers.add_parser("stop", help="Stop orchestrator started with start")
    stop.add_argument(
        "--pid-file",
        default="orchestrator.pid",
        help="File containing orchestrator PID",
    )

    return parser


def main(argv=None):
    """Run the orchestrator using arguments from ``argv``."""
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command is None:
        args.command = "run"

    configure_logging()

    setup_telemetry()

    if args.command == "start":
        cmd = [sys.executable, "-m", "core.cli", "run", "--memory", args.memory]
        proc = subprocess.Popen(cmd)
        Path(args.pid_file).write_text(str(proc.pid))
        print(f"Orchestrator started with PID {proc.pid}")
        return 0

    if args.command == "stop":
        pid_path = Path(args.pid_file)
        if not pid_path.exists():
            print("PID file not found", file=sys.stderr)
            return 1
        pid = int(pid_path.read_text())
        try:
            os.kill(pid, signal.SIGTERM)
        except ProcessLookupError:
            print("Process not running")
        pid_path.unlink()
        print("Orchestrator stopped")
        return 0

    memory = Memory(Path(args.memory))
    try:
        memory.save(memory.load())
    except Exception as exc:  # pragma: no cover - unexpected I/O errors
        print(f"Error accessing memory: {exc}", file=sys.stderr)
        return 1

    planner = Planner()
    executor = Executor()
    reflector = Reflector()
    auditor = SelfAuditor()
    orchestrator = Orchestrator(planner, executor, reflector, memory, auditor)
    print("Orchestrator running")
    orchestrator.run()
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
