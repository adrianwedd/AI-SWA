"""Reinforcement Learning Hyper-Heuristic agent for task prioritization."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import random
from pathlib import Path

from core.task import Task
from core.code_llm import CodeLLM
from .wsjf import wsjf_score
from .vision_engine import RLAgent


@dataclass
class RLHyperHeuristicAgent(RLAgent):
    """Simple RL-based hyper-heuristic adjusting WSJF weighting."""

    heuristic_weights: Dict[str, float] = field(default_factory=lambda: {"wsjf": 1.0})
    exploration: float = 0.05

    def __init__(
        self,
        history_path: Optional[Path] = None,
        training_path: Optional[Path] = None,
        code_model: Optional[CodeLLM] = None,
        heuristic_weights: Optional[Dict[str, float]] = None,
        exploration: float = 0.05,
    ) -> None:
        super().__init__(history_path=history_path, training_path=training_path, code_model=code_model)
        self.heuristic_weights = heuristic_weights or {"wsjf": 1.0}
        self.exploration = exploration

    def suggest(self, tasks: List[Task]) -> List[Task]:
        """Return tasks ordered by weighted WSJF score with optional noise."""
        scored = []
        for t in tasks:
            score = self.heuristic_weights["wsjf"] * wsjf_score(t)
            score += random.random() * self.exploration
            scored.append((score, t))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [t for _, t in scored]

    def train(self, metrics: Dict[str, float]) -> float:
        """Adjust heuristic weight based on provided metrics and return reward."""
        reward = super().train(metrics)
        delta = metrics.get("gain", 0.0)
        self.heuristic_weights["wsjf"] += 0.1 * delta
        return reward
