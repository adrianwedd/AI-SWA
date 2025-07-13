"""Apply Grafana dashboards from JSON files."""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Iterable

import requests

from core.log_utils import configure_logging

GRAFANA_URL = os.getenv("GRAFANA_URL", "http://localhost:3000")
GRAFANA_API_KEY = os.getenv("GRAFANA_API_KEY")
DASHBOARD_DIR = Path(os.getenv("DASHBOARD_DIR", "grafana/dashboards"))


def iter_dashboards(directory: Path) -> Iterable[Path]:
    for path in directory.glob("*.json"):
        if path.is_file():
            yield path


def apply_dashboard(path: Path) -> None:
    if not GRAFANA_API_KEY:
        raise RuntimeError("GRAFANA_API_KEY not set")
    data = json.loads(path.read_text())
    payload = {"dashboard": data, "overwrite": True}
    headers = {"Authorization": f"Bearer {GRAFANA_API_KEY}", "Content-Type": "application/json"}
    response = requests.post(
        f"{GRAFANA_URL}/api/dashboards/db",
        json=payload,
        headers=headers,
        timeout=10,
    )
    response.raise_for_status()
    logging.info("Applied %s", path.name)


def main() -> None:
    configure_logging()
    for path in iter_dashboards(DASHBOARD_DIR):
        apply_dashboard(path)


if __name__ == "__main__":
    main()
