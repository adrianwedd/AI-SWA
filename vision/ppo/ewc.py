from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict


@dataclass
class EWC:
    """Minimal Elastic Weight Consolidation regularizer."""

    lambda_: float = 0.4
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

    def update_importance(self, params: Dict[str, float]) -> None:
        """Update Fisher information approximation."""
        for name, value in params.items():
            self.fisher[name] = self.fisher.get(name, 0.0) + value ** 2
        self.opt_params = params.copy()
