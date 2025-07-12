from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, Optional, Tuple

import math


@dataclass
class EWC:
    """Minimal Elastic Weight Consolidation regularizer."""

    lambda_: float = 10.0
    fisher: Dict[str, float] = field(default_factory=dict)
    opt_params: Dict[str, float] = field(default_factory=dict)

    def compute_penalty(self, params: Dict[str, float]) -> float:
        """Return EWC penalty for ``params``."""
        penalty = 0.0
        for name, value in params.items():
            importance = self.fisher.get(name, 0.0)
            opt = self.opt_params.get(name, 0.0)
            penalty += importance * (value - opt) ** 2
        return self.lambda_ * penalty

    def _estimate_fisher(
        self,
        batch: Iterable[Tuple[Dict[str, float], int, float, Dict[str, float], bool, float]],
        params: Dict[str, float],
    ) -> Dict[str, float]:
        """Return diagonal Fisher information estimate for ``params``."""
        fisher: Dict[str, float] = {k: 0.0 for k in params}
        count = 0
        for state, action, _r, _ns, _done, _lp in batch:
            z = sum(state.get(k, 0.0) * params.get(k, 0.0) for k in state)
            p = 1.0 / (1.0 + math.exp(-z))
            for k, v in state.items():
                grad = (1 - p) * v if action == 1 else -p * v
                fisher[k] += grad ** 2
            count += 1
        if count:
            for k in fisher:
                fisher[k] /= count
        return fisher

    def update_importance(
        self,
        params: Dict[str, float],
        batch: Optional[
            Iterable[Tuple[Dict[str, float], int, float, Dict[str, float], bool, float]]
        ] = None,
    ) -> None:
        """Update Fisher information approximation."""
        if batch is not None:
            fisher = self._estimate_fisher(batch, params)
        else:
            fisher = {name: value ** 2 for name, value in params.items()}
        for name, value in fisher.items():
            self.fisher[name] = self.fisher.get(name, 0.0) + value * 10
        self.opt_params = params.copy()
