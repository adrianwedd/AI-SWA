from __future__ import annotations

from typing import Dict, Optional

from pathlib import Path

from core.observability import MetricsProvider


class StateBuilder:
    """Generate a normalized numerical state from metrics and logs."""

    def __init__(
        self, metrics_provider: MetricsProvider, logs_path: Optional[Path] = None
    ) -> None:
        self.metrics_provider = metrics_provider
        self.logs_path = Path(logs_path) if logs_path else None

    # --------------------------------------------------------------
    def _log_metrics(self) -> Dict[str, float]:
        if not self.logs_path:
            return {}
        path = self.logs_path
        text = ""
        if path.is_dir():
            for p in path.glob("*.log"):
                try:
                    text += p.read_text(errors="ignore") + "\n"
                except Exception:
                    continue
        elif path.exists():
            try:
                text = path.read_text(errors="ignore")
            except Exception:
                text = ""
        lines = text.splitlines()
        err = sum(1 for line in lines if "error" in line.lower())
        return {"log_lines": float(len(lines)), "error_lines": float(err)}

    def build(self) -> Dict[str, float]:
        metrics = self.metrics_provider.collect()
        numeric = {
            k: float(v)
            for k, v in metrics.items()
            if isinstance(v, (int, float))
        }
        numeric.update(self._log_metrics())
        if numeric:
            max_abs = max(abs(v) for v in numeric.values()) or 1.0
            numeric = {k: v / max_abs for k, v in numeric.items()}
        return numeric

    def vector(self) -> list[float]:
        """Return a sorted list of numeric metric values."""
        state = self.build()
        return [state[k] for k in sorted(state.keys())]
