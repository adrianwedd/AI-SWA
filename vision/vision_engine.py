from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Optional
import json

from core.task import Task


def wsjf_score(task: Task) -> float:
    """Return Weighted Shortest Job First score for ``task``."""
    cod = (
        getattr(task, "user_business_value", 0)
        + getattr(task, "time_criticality", 0)
        + getattr(task, "risk_reduction", 0)
    )
    job_size = getattr(task, "job_size", 1)
    if job_size == 0:
        job_size = 1
    return cod / job_size


@dataclass
class VisionEngine:
    """Prioritize tasks using WSJF with optional RL refinement."""

    rl_agent: Optional[RLAgent] = None
    shadow_mode: bool = True

    def prioritize(self, tasks: List[Task]) -> List[Task]:
        """Return ``tasks`` ordered by WSJF score."""
        scored = [(wsjf_score(t), t) for t in tasks]
        scored.sort(key=lambda x: x[0], reverse=True)
        ordered = [t for _, t in scored]
        if self.rl_agent:
            ordered = self._maybe_refine_with_rl(ordered)
        return ordered

    def _maybe_refine_with_rl(self, tasks: List[Task]) -> List[Task]:
        suggestions = self.rl_agent.suggest(tasks)
        if self.shadow_mode or self.rl_agent.authority <= 0:
            # Log but do not alter ordering
            self.rl_agent.record_shadow_result(tasks, suggestions)
            return tasks

        if self.rl_agent.authority >= 1:
            return suggestions

        # Apply RL ordering to a fraction of tasks equal to authority
        n = int(len(tasks) * self.rl_agent.authority)
        top_rl = suggestions[:n]
        remaining = [t for t in tasks if t not in top_rl]
        return top_rl + remaining


class RLAgent:
    """Minimal stub of an RL agent for prioritization."""

    def __init__(
        self,
        history_path: Optional[Path] = None,
        training_path: Optional[Path] = None,
    ) -> None:
        self.history: List[Dict[str, List[int]]] = []
        self.training_data: List[Dict[str, float]] = []
        self.history_path = Path(history_path) if history_path else None
        self.training_path = Path(training_path) if training_path else None
        self.authority: float = 0.0

    def suggest(self, tasks: List[Task]) -> List[Task]:
        """Return refined ordering. Currently identity function."""
        return tasks

    def record_shadow_result(self, baseline: List[Task], suggestion: List[Task]) -> None:
        """Store comparison between baseline and suggestion for offline training."""
        entry = {
            "baseline": [t.id for t in baseline],
            "suggestion": [t.id for t in suggestion],
        }
        self.history.append(entry)
        if self.history_path:
            with self.history_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")

    def train(self, metrics: Dict[str, float]) -> float:
        """Collect ``metrics`` for offline training and return reward."""
        reward = sum(
            v for v in metrics.values() if isinstance(v, (int, float))
        )
        self.training_data.append(metrics)
        if self.training_path:
            with self.training_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(metrics) + "\n")
        return float(reward)

    def update_authority(self, performance_gain: float, threshold: float = 0.05) -> None:
        """Increase authority when ``performance_gain`` exceeds ``threshold``."""
        if performance_gain > threshold:
            self.authority = min(1.0, self.authority + performance_gain)
