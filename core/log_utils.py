"""Logging utilities for consistent configuration."""

from __future__ import annotations

import logging
from logging.config import fileConfig
from pathlib import Path
from typing import Optional

DEFAULT_CONFIG_PATH = Path(__file__).resolve().parents[1] / "logging.conf"


def configure_logging(
    logfile: Optional[Path] = None,
    level: int = logging.INFO,
    config_path: Optional[Path] = None,
) -> None:
    """Configure the root logger with a standard format.

    Parameters
    ----------
    logfile:
        Optional path to log file. If omitted, logs are sent to stderr.
    level:
        Logging level. Defaults to ``logging.INFO``.
    """
    if logging.getLogger().hasHandlers():
        return

    cfg = Path(config_path or DEFAULT_CONFIG_PATH)
    if cfg.exists():
        fileConfig(cfg, disable_existing_loggers=False)
        if logfile:
            for handler in logging.getLogger().handlers:
                if hasattr(handler, "baseFilename"):
                    handler.baseFilename = str(logfile)
        logging.getLogger().setLevel(level)
    else:
        params = {
            "level": level,
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        }
        if logfile:
            params["filename"] = str(logfile)
        logging.basicConfig(**params)
