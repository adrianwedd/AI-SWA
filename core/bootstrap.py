"""Bootstrap the SelfArchitectAI environment and validate tasks."""

import json
import logging
import os
import sys
import sentry_sdk
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import yaml
from jsonschema import validate, ValidationError
from core.memory import TASK_SCHEMA
from core.log_utils import configure_logging


def create_logfile_path(base_dir: Path = Path("logs")) -> Path:
    """Return a timestamped logfile path inside ``base_dir``."""
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return base_dir / f"bootstrap-{timestamp}.log"


def setup_logging(base_dir: Path = Path("logs")) -> Path:
    """Create logging directory and configure root logger.

    Parameters
    ----------
    base_dir:
        Directory in which the logfile is created.

    Returns
    -------
    pathlib.Path
        Path to the created logfile. Exits with code ``2`` if the
        directory cannot be created.
    """
    logfile = create_logfile_path(base_dir)
    try:
        logfile.parent.mkdir(exist_ok=True)
        configure_logging(logfile=logfile)
        logfile.touch(exist_ok=True)
    except OSError as exc:
        logging.error("[ERROR] %s", exc)
        sys.exit(2)
    return logfile


def select_next_task(tasks):
    """Return the highest priority pending task or ``None`` if absent."""
    pending = [t for t in tasks if t.get("status") == "pending"]
    if not pending:
        return None
    return sorted(pending, key=lambda x: x.get("priority", 5))[0]


def load_schema_and_tasks(path: Path):
    """Return JSON schema and task list from ``tasks.yml``.

    Parameters
    ----------
    path:
        Location of the ``tasks.yml`` file.

    Returns
    -------
    tuple
        Parsed JSON schema and list of task dictionaries. Exits with code
        ``2`` if the file cannot be read or ``1`` for parsing errors. If no
        ``# jsonschema:`` header is present in the file, the default schema in
        ``core.memory.TASK_SCHEMA`` is used.
    """
    try:
        text = path.read_text()
    except OSError as exc:
        logging.error("[ERROR] %s", exc)
        sys.exit(2)

    schema_lines = []
    task_lines = []
    lines = text.splitlines()
    schema_started = False
    for line in lines:
        if line.startswith("# jsonschema:"):
            schema_started = True
            continue
        if schema_started and line.startswith("#"):
            schema_lines.append(line[1:].lstrip())
            continue
        task_lines.append(line)

    if schema_lines:
        schema_str = "\n".join(schema_lines)
        try:
            schema = json.loads(schema_str)
        except json.JSONDecodeError as exc:
            logging.error("[ERROR] %s", exc)
            sys.exit(1)
    else:
        schema = TASK_SCHEMA

    try:
        tasks = yaml.safe_load("\n".join(task_lines)) or []
    except yaml.YAMLError as exc:
        logging.error("[ERROR] %s", exc)
        sys.exit(1)

    return schema, tasks


def main():
    """Bootstrap the system by validating ``tasks.yml``."""
    sentry_sdk.init(dsn=os.getenv("SENTRY_DSN"))
    setup_logging()
    schema, tasks = load_schema_and_tasks(Path("tasks.yml"))

    try:
        validate(instance=tasks, schema=schema)
    except ValidationError as exc:
        logging.error("[ERROR] %s", exc)
        sys.exit(1)

    task = select_next_task(tasks)
    if not task:
        logging.info("No pending tasks found")
        sys.exit(0)

    logging.info("Next task: %s", task)
    sys.exit(0)


if __name__ == "__main__":
    main()
