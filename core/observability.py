from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Dict, Optional

from .log_utils import configure_logging


class MetricsProvider:
    """Simple provider for observability metrics."""

    def __init__(self, metrics_path: Optional[Path] = None) -> None:
        configure_logging()
        self.metrics_path = Path(metrics_path or "metrics.json")
        self.logger = logging.getLogger(__name__)

    def collect(self) -> Dict:
        """Return metrics from ``metrics_path`` if available."""
        if not self.metrics_path.exists():
            self.logger.info("Metrics file %s not found", self.metrics_path)
            return {}
        try:
            with self.metrics_path.open("r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as exc:  # pragma: no cover - IO issues
            self.logger.warning("Failed to read metrics: %s", exc)
            return {}

