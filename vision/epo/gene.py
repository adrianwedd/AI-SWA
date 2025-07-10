from __future__ import annotations

from dataclasses import dataclass
import json
import random
from pathlib import Path
from typing import Tuple


@dataclass
class Gene:
    """Hyperparameters and architecture for a PPO agent."""

    architecture: Tuple[int, ...] = (64,)
    learning_rate: float = 0.001
    clip_epsilon: float = 0.2
    gamma: float = 0.99

    def mutate(self) -> Gene:
        """Return a slightly modified copy of this gene."""
        layers = [
            max(1, min(256, l + random.randint(-8, 8))) for l in self.architecture
        ]
        return Gene(
            architecture=tuple(layers),
            learning_rate=max(1e-5, self.learning_rate * random.uniform(0.8, 1.2)),
            clip_epsilon=min(1.0, max(0.01, self.clip_epsilon + random.uniform(-0.05, 0.05))),
            gamma=min(0.999, max(0.5, self.gamma + random.uniform(-0.05, 0.05))),
        )

    def crossover(self, other: Gene) -> Gene:
        """Combine attributes from this gene and ``other``."""
        arch = tuple(
            random.choice([a, b]) for a, b in zip(self.architecture, other.architecture)
        )
        return Gene(
            architecture=arch,
            learning_rate=random.choice([self.learning_rate, other.learning_rate]),
            clip_epsilon=random.choice([self.clip_epsilon, other.clip_epsilon]),
            gamma=random.choice([self.gamma, other.gamma]),
        )

    @property
    def hidden_dim(self) -> int:
        """Convenience accessor for the last layer size."""
        return self.architecture[-1]

    def to_dict(self) -> dict:
        return {
            "architecture": list(self.architecture),
            "learning_rate": self.learning_rate,
            "clip_epsilon": self.clip_epsilon,
            "gamma": self.gamma,
        }

    def to_json(self, path: Path) -> None:
        with path.open("w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f)

    @classmethod
    def from_dict(cls, data: dict) -> Gene:
        return cls(
            architecture=tuple(data["architecture"]),
            learning_rate=data["learning_rate"],
            clip_epsilon=data["clip_epsilon"],
            gamma=data["gamma"],
        )

    @classmethod
    def from_json(cls, path: Path) -> Gene:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)
