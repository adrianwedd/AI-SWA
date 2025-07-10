from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict


@dataclass
class CriticNetwork:
    """Linear value approximator."""

    learning_rate: float = 0.01
    weights: Dict[str, float] = field(default_factory=dict)

    def value(self, state: Dict[str, float]) -> float:
        """Return the estimated value for ``state``."""
        return sum(state.get(k, 0.0) * self.weights.get(k, 0.0) for k in state.keys())

    def update(self, state: Dict[str, float], target: float) -> None:
        """Update weights toward ``target`` value."""
        v = self.value(state)
        error = target - v
        for k, v_s in state.items():
            self.weights[k] = self.weights.get(k, 0.0) + self.learning_rate * error * v_s
