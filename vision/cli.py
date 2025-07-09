"""Command line interface for WSJF task ranking."""

import argparse
import sys
import logging
from pathlib import Path
from types import SimpleNamespace

import yaml

from .vision_engine import wsjf_score


def build_parser() -> argparse.ArgumentParser:
    """Return argument parser for the CLI."""
    parser = argparse.ArgumentParser(description="Rank tasks using WSJF scoring")
    parser.add_argument(
        "tasks_file",
        help="Path to YAML file containing tasks with WSJF fields",
    )
    return parser


def main(argv=None) -> int:
    """Run the WSJF ranking CLI."""
    parser = build_parser()
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO)
    path = Path(args.tasks_file)
    if not path.exists():
        logging.error("Tasks file not found: %s", path)
        return 1
    data = yaml.safe_load(path.read_text()) or []
    tasks = [SimpleNamespace(**item) for item in data]
    scored = [
        {"id": item.get("id"), "wsjf": wsjf_score(task)}
        for item, task in zip(data, tasks)
    ]
    scored.sort(key=lambda x: x["wsjf"], reverse=True)
    yaml.safe_dump(scored, sys.stdout, sort_keys=False)
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
