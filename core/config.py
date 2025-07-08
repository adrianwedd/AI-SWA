"""Configuration loader for AI-SWA services."""

from __future__ import annotations

import os
from pathlib import Path
import yaml

DEFAULT_CONFIG = {
    "broker": {"db_path": "tasks.db", "metrics_port": 9000},
    "worker": {
        "broker_url": "http://broker:8000",
        "metrics_port": 9001,
        "concurrency": 2,
    },
    "node": {"host": "localhost", "port": 50051},
    "security": {
        "api_key": None,
        "api_tokens": None,
        "api_key_env": "API_KEY",
        "api_tokens_env": "API_TOKENS",
        "plugin_signing_key": None,
        "plugin_signing_key_env": "PLUGIN_SIGNING_KEY",
        "plugin_policy_file": "plugins/policy.json",
        "plugin_policy_file_env": "PLUGIN_POLICY_FILE",
    },
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
    if "WORKER_CONCURRENCY" in os.environ:
        cfg["worker"]["concurrency"] = int(os.environ["WORKER_CONCURRENCY"])
    if "NODE_HOST" in os.environ:
        cfg["node"]["host"] = os.environ["NODE_HOST"]
    if "NODE_PORT" in os.environ:
        cfg["node"]["port"] = int(os.environ["NODE_PORT"])
    if "METRICS_PORT" in os.environ:
        port = int(os.environ["METRICS_PORT"])
        cfg["broker"]["metrics_port"] = port
        cfg["worker"]["metrics_port"] = port
    sec = cfg["security"]

    if "API_KEY" in os.environ:
        sec["api_key"] = os.environ["API_KEY"]
    if "API_TOKENS" in os.environ:
        sec["api_tokens"] = os.environ["API_TOKENS"]
    if "PLUGIN_SIGNING_KEY" in os.environ:
        sec["plugin_signing_key"] = os.environ["PLUGIN_SIGNING_KEY"]
    if "PLUGIN_POLICY_FILE" in os.environ:
        sec["plugin_policy_file"] = os.environ["PLUGIN_POLICY_FILE"]

    env_name = sec.get("api_key_env")
    if env_name and env_name in os.environ:
        sec["api_key"] = os.environ[env_name]
    env_name = sec.get("api_tokens_env")
    if env_name and env_name in os.environ:
        sec["api_tokens"] = os.environ[env_name]
    env_name = sec.get("plugin_signing_key_env")
    if env_name and env_name in os.environ:
        sec["plugin_signing_key"] = os.environ[env_name]
    env_name = sec.get("plugin_policy_file_env")
    if env_name and env_name in os.environ:
        sec["plugin_policy_file"] = os.environ[env_name]

    return cfg
