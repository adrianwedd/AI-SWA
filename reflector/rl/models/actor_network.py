from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict
import math


@dataclass
class ActorNetwork:
    """Lightweight actor approximated by logistic regression."""

    learning_rate: float = 0.01
    weights: Dict[str, float] = field(default_factory=dict)

    def probability(self, state: Dict[str, float]) -> float:
        """Return probability of taking action 1 for ``state``."""
        z = sum(state.get(k, 0.0) * self.weights.get(k, 0.0) for k in state.keys())
        return 1.0 / (1.0 + math.exp(-z))

    def update(
        self,
        state: Dict[str, float],
        action: int,
        advantage: float,
        old_log_prob: float,
        clip_epsilon: float,
        penalty_grad: Dict[str, float] | None = None,
    ) -> None:
        """Update weights using PPO clipped objective with optional EWC."""
        p = self.probability(state)
        log_prob = math.log(p if action == 1 else 1.0 - p + 1e-8)
        ratio = math.exp(log_prob - old_log_prob)
        clipped_ratio = max(min(ratio, 1 + clip_epsilon), 1 - clip_epsilon)
        factor = min(ratio, clipped_ratio) * advantage
        for k, v in state.items():
            grad_log_prob = (1 - p) * v if action == 1 else -p * v
            update = self.learning_rate * factor * grad_log_prob
            if penalty_grad is not None:
                update -= penalty_grad.get(k, 0.0)
            self.weights[k] = self.weights.get(k, 0.0) + update
