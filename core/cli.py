import argparse
import logging
import os
import signal
import subprocess
import sys
from pathlib import Path

from .orchestrator import Orchestrator
from .memory import Memory
from dataclasses import asdict
import yaml
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

    list_cmd = subparsers.add_parser("list", help="List tasks from tasks.yml")
    list_cmd.add_argument(
        "--tasks",
        default="tasks.yml",
        help="Path to tasks.yml",
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
        logging.error("Config not found: %s", path)
        return False
    return True


def _run_orchestrator(config: Path) -> int:
    if not _check_config(config):
        return 1
    setup_telemetry()
    memory = Memory(Path("state.json"))
    try:
        memory.save(memory.load())
    except Exception as exc:  # pragma: no cover - unexpected I/O errors
        logging.error("Error accessing memory: %s", exc)
        return 1

    planner = Planner()
    executor = Executor()
    reflector = Reflector()
    auditor = SelfAuditor()
    orchestrator = Orchestrator(planner, executor, reflector, memory, auditor)
    logging.info("Orchestrator running")
    orchestrator.run()
    return 0


def main(argv=None) -> int:
    """CLI entry point."""
    parser = build_parser()
    args = parser.parse_args(argv)
    configure_logging(level=_logging_level(args.verbose))
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
        logging.info("Orchestrator started with PID %s", proc.pid)
        return 0

    if args.command == "stop":
        pid_path = Path(args.pid_file)
        if not pid_path.exists():
            logging.error("PID file not found")
            return 1
        pid = int(pid_path.read_text())
        try:
            os.kill(pid, signal.SIGTERM)
        except ProcessLookupError:
            logging.info("Process not running")
        pid_path.unlink(missing_ok=True)
        logging.info("Orchestrator stopped")
        return 0

    if args.command == "status":
        pid_path = Path(args.pid_file)
        if not pid_path.exists():
            logging.error("Not running")
            return 1
        pid = int(pid_path.read_text())
        try:
            os.kill(pid, 0)
        except OSError:
            logging.error("Not running")
            pid_path.unlink(missing_ok=True)
            return 1
        logging.info("Orchestrator running with PID %s", pid)
        return 0

    if args.command == "list":
        memory = Memory(Path("state.json"))
        tasks = memory.load_tasks(args.tasks)
        data = [asdict(t) for t in tasks]
        yaml.safe_dump(data, sys.stdout, sort_keys=False)
        return 0

    if args.command == "_run":
        return _run_orchestrator(Path(args.config))

    parser.print_help()
    return 1


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
