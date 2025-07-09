"""Simple Evaluator that records critiques of tasks."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List
import yaml


class Evaluator:
    """Provide lightweight scoring and reflection for tasks."""

    def __init__(self, log_path: Path = Path("critiques.yml")) -> None:
        self.log_path = Path(log_path)

    # ------------------------------------------------------------------
    def critique(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Return a critique dictionary with a score and notes."""
        score = 10
        notes: List[str] = []

        if item.get("status") != "done":
            score -= 5
            notes.append("task incomplete")

        desc = str(item.get("description", "")).lower()
        if "error" in desc:
            score -= 5
            notes.append("error mentioned")

        return {"id": item.get("id"), "score": max(0, score), "notes": "; ".join(notes)}

    # ------------------------------------------------------------------
    def reflect(self, tasks: List[Dict[str, Any]]) -> Dict[int, Dict[str, Any]]:
        """Critique each task and persist the results."""
        critiques = {t.get("id"): self.critique(t) for t in tasks}
        self._save_critiques(critiques)
        return critiques

    # ------------------------------------------------------------------
    def _load_critiques(self) -> Dict[str, Dict[str, Any]]:
        if not self.log_path.exists():
            return {}
        with self.log_path.open("r") as fh:
            return yaml.safe_load(fh) or {}

    # ------------------------------------------------------------------
    def _save_critiques(self, critiques: Dict[int, Dict[str, Any]]) -> None:
        data = self._load_critiques()
        for k, v in critiques.items():
            data[str(k)] = v
        with self.log_path.open("w") as fh:
            yaml.safe_dump(data, fh, sort_keys=False)
