from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List, Tuple
import random


@dataclass
class ReplayBuffer:
    """Fixed-size experience replay buffer with configurable sampling."""

    capacity: int
    strategy: str = "uniform"
    buffer: List[Tuple[Any, ...]] = field(default_factory=list)

    def add(self, transition: Tuple[Any, ...]) -> None:
        """Store ``transition`` and evict oldest when over capacity."""
        if len(self.buffer) >= self.capacity:
            self.buffer.pop(0)
        self.buffer.append(transition)

    def sample(self, batch_size: int) -> List[Tuple[Any, ...]]:
        """Return a mini-batch of experiences using ``strategy``."""
        if not self.buffer:
            return []
        n = min(batch_size, len(self.buffer))
        if self.strategy == "fifo":
            return self.buffer[-n:]
        return random.sample(self.buffer, n)

    def __len__(self) -> int:  # pragma: no cover - trivial
        return len(self.buffer)
