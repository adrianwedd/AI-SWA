from __future__ import annotations

from dataclasses import dataclass
import random


@dataclass
class Gene:
    """Hyperparameters defining a PPO agent configuration."""

    hidden_dim: int = 64
    learning_rate: float = 0.001
    clip_epsilon: float = 0.2
    gamma: float = 0.99

    def mutate(self) -> Gene:
        """Return a slightly modified copy of this gene."""
        return Gene(
            hidden_dim=max(1, self.hidden_dim + random.randint(-8, 8)),
            learning_rate=max(1e-5, self.learning_rate * random.uniform(0.8, 1.2)),
            clip_epsilon=min(1.0, max(0.01, self.clip_epsilon + random.uniform(-0.05, 0.05))),
            gamma=min(0.999, max(0.5, self.gamma + random.uniform(-0.05, 0.05))),
        )

    def crossover(self, other: Gene) -> Gene:
        """Combine attributes from this gene and ``other``."""
        return Gene(
            hidden_dim=random.choice([self.hidden_dim, other.hidden_dim]),
            learning_rate=random.choice([self.learning_rate, other.learning_rate]),
            clip_epsilon=random.choice([self.clip_epsilon, other.clip_epsilon]),
            gamma=random.choice([self.gamma, other.gamma]),
        )
