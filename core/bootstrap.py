"""Bootstrap the AI-SWA environment and validate tasks."""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import yaml
from jsonschema import validate, ValidationError
from core.memory import TASK_SCHEMA
from core.log_utils import configure_logging


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
    """Bootstrap the system by validating ``tasks.yml``.

    Returns exit codes ``0`` on success, ``1`` for validation errors and ``2``
    for filesystem issues.
    """
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    logfile = Path("logs") / f"bootstrap-{timestamp}.log"
    try:
        logfile.parent.mkdir(exist_ok=True)
        configure_logging(logfile=logfile)
    except OSError as exc:
        print(f"[ERROR] {exc}")
        sys.exit(2)

    schema, tasks = load_schema_and_tasks(Path("tasks.yml"))

    try:
        validate(instance=tasks, schema=schema)
    except ValidationError as exc:
        logging.error("[ERROR] %s", exc)
        sys.exit(1)

    pending = [t for t in tasks if t.get("status") == "pending"]
    if not pending:
        logging.info("No pending tasks found")
        sys.exit(0)

    task = sorted(pending, key=lambda x: x.get("priority", 5))[0]
    logging.info("Next task: %s", task)
    sys.exit(0)


if __name__ == "__main__":
    main()
