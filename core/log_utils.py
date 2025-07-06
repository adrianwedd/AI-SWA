"""Logging utilities for consistent configuration."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional


def configure_logging(logfile: Optional[Path] = None, level: int = logging.INFO) -> None:
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

    params = {
        "level": level,
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    }
    if logfile:
        params["filename"] = str(logfile)
    logging.basicConfig(**params)
