import argparse
import logging
import os
import signal
import subprocess
import sys
from pathlib import Path

from .orchestrator import Orchestrator
from .memory import Memory
from .planner import Planner
from .executor import Executor
from .reflector import Reflector
from .self_auditor import SelfAuditor
from .telemetry import setup_telemetry
from .log_utils import configure_logging


def build_parser() -> argparse.ArgumentParser:
    """Return argument parser for the CLI."""
    parser = argparse.ArgumentParser(description="AI-SWA orchestration CLI")
    parser.add_argument(
        "--config",
        default="config.yaml",
        help="Path to configuration file",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Increase verbosity",
    )
    subparsers = parser.add_subparsers(dest="command")

    start = subparsers.add_parser("start", help="Start orchestrator in background")
    start.add_argument(
        "--pid-file",
        default="orchestrator.pid",
        help="File to store orchestrator PID",
    )

    stop = subparsers.add_parser("stop", help="Stop orchestrator started with start")
    stop.add_argument(
        "--pid-file",
        default="orchestrator.pid",
        help="File containing orchestrator PID",
    )

    status = subparsers.add_parser("status", help="Show orchestrator status")
    status.add_argument(
        "--pid-file",
        default="orchestrator.pid",
        help="File containing orchestrator PID",
    )

    # Internal command used by "start"; not exposed in docs
    run = subparsers.add_parser("_run")
    run.add_argument("--config", default="config.yaml")
    run.add_argument("-v", "--verbose", action="count", default=0)

    return parser


def _logging_level(verbosity: int) -> int:
    return logging.DEBUG if verbosity else logging.INFO


def _check_config(path: Path) -> bool:
    if not path.exists():
        print(f"Config not found: {path}", file=sys.stderr)
        return False
    return True


def _run_orchestrator(config: Path, verbosity: int) -> int:
    if not _check_config(config):
        return 1
    configure_logging(level=_logging_level(verbosity))
    setup_telemetry()
    memory = Memory(Path("state.json"))
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


def main(argv=None) -> int:
    """CLI entry point."""
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.command:
        parser.print_help()
        return 1

    if args.command == "start":
        config = Path(args.config)
        if not _check_config(config):
            return 1
        cmd = [sys.executable, "-m", "ai_swa.orchestrator", "_run", "--config", str(config)]
        cmd += ["-v"] * args.verbose
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
        pid_path.unlink(missing_ok=True)
        print("Orchestrator stopped")
        return 0

    if args.command == "status":
        pid_path = Path(args.pid_file)
        if not pid_path.exists():
            print("Not running")
            return 1
        pid = int(pid_path.read_text())
        try:
            os.kill(pid, 0)
        except OSError:
            print("Not running")
            pid_path.unlink(missing_ok=True)
            return 1
        print(f"Orchestrator running with PID {pid}")
        return 0

    if args.command == "_run":
        return _run_orchestrator(Path(args.config), args.verbose)

    parser.print_help()
    return 1


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
