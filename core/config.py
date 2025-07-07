"""Configuration loader for AI-SWA services."""

from __future__ import annotations

import os
from pathlib import Path
import yaml

DEFAULT_CONFIG = {
    "broker": {"db_path": "tasks.db", "metrics_port": 9000},
    "worker": {"broker_url": "http://broker:8000", "metrics_port": 9001},
    "node": {"host": "localhost", "port": 50051},
    "security": {"api_key": None, "api_tokens": None, "plugin_signing_key": None},
}

CONFIG_PATH = Path(__file__).resolve().parents[1] / "config.yaml"


def load_config(path: str | Path | None = None) -> dict:
    """Return configuration merged with environment overrides."""
    cfg_path = Path(os.getenv("CONFIG_FILE", path or CONFIG_PATH))
    data: dict = {}
    if cfg_path.exists():
        with cfg_path.open() as f:
            data = yaml.safe_load(f) or {}
    cfg = {
        "broker": {**DEFAULT_CONFIG["broker"], **data.get("broker", {})},
        "worker": {**DEFAULT_CONFIG["worker"], **data.get("worker", {})},
        "node": {**DEFAULT_CONFIG["node"], **data.get("node", {})},
        "security": {**DEFAULT_CONFIG["security"], **data.get("security", {})},
    }

    if "DB_PATH" in os.environ:
        cfg["broker"]["db_path"] = os.environ["DB_PATH"]
    if "BROKER_URL" in os.environ:
        cfg["worker"]["broker_url"] = os.environ["BROKER_URL"]
    if "BROKER_METRICS_PORT" in os.environ:
        cfg["broker"]["metrics_port"] = int(os.environ["BROKER_METRICS_PORT"])
    if "WORKER_METRICS_PORT" in os.environ:
        cfg["worker"]["metrics_port"] = int(os.environ["WORKER_METRICS_PORT"])
    if "NODE_HOST" in os.environ:
        cfg["node"]["host"] = os.environ["NODE_HOST"]
    if "NODE_PORT" in os.environ:
        cfg["node"]["port"] = int(os.environ["NODE_PORT"])
    if "METRICS_PORT" in os.environ:
        port = int(os.environ["METRICS_PORT"])
        cfg["broker"]["metrics_port"] = port
        cfg["worker"]["metrics_port"] = port
    if "API_KEY" in os.environ:
        cfg["security"]["api_key"] = os.environ["API_KEY"]
    if "API_TOKENS" in os.environ:
        cfg["security"]["api_tokens"] = os.environ["API_TOKENS"]
    if "PLUGIN_SIGNING_KEY" in os.environ:
        cfg["security"]["plugin_signing_key"] = os.environ["PLUGIN_SIGNING_KEY"]

    return cfg
