
"""Move completed tasks from ``tasks.yml`` to ``tasks_archive.yml``.

This helper preserves any comment header and appends archived tasks to the
archive file.  It is intended to keep ``tasks.yml`` concise.  Run periodically
or whenever tasks accumulate.
"""

import argparse
from pathlib import Path
import yaml


def load_tasks_with_header(path: str):
    p = Path(path)
    if not p.exists():
        return [], []
    lines = p.read_text().splitlines()
    header = []
    i = 0
    while i < len(lines) and lines[i].startswith("#"):
        header.append(lines[i])
        i += 1
    tasks = yaml.safe_load("\n".join(lines[i:])) or []
    return header, tasks


def save_tasks_with_header(path: str, header, tasks) -> None:
    p = Path(path)
    with p.open("w") as fh:
        if header:
            fh.write("\n".join(header) + "\n")
        yaml.safe_dump(tasks, fh, sort_keys=False)


def archive_tasks(tasks_path: str = "tasks.yml", archive_path: str = "tasks_archive.yml") -> int:
    header, tasks = load_tasks_with_header(tasks_path)
    done = [t for t in tasks if t.get("status") == "done"]
    remaining = [t for t in tasks if t.get("status") != "done"]

    save_tasks_with_header(tasks_path, header, remaining)

    arch_header, archived = load_tasks_with_header(archive_path)
    archived.extend(done)
    save_tasks_with_header(archive_path, arch_header, archived)

    return len(done)


def main():
    parser = argparse.ArgumentParser(description="Archive completed tasks")
    parser.add_argument("--tasks", default="tasks.yml", help="Path to tasks.yml")
    parser.add_argument(
        "--archive", default="tasks_archive.yml", help="Archive file path"
    )
    args = parser.parse_args()
    count = archive_tasks(args.tasks, args.archive)
    print(f"Archived {count} tasks.")


if __name__ == "__main__":
    main()
