from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Tuple, Any
import random


@dataclass
class ReplayBuffer:
    """Fixed-size experience replay buffer."""

    capacity: int
    buffer: List[Tuple[Any, ...]] = field(default_factory=list)

    def add(self, transition: Tuple[Any, ...]) -> None:
        """Store ``transition`` and evict oldest when over capacity."""
        if len(self.buffer) >= self.capacity:
            self.buffer.pop(0)
        self.buffer.append(transition)

    def sample(self, batch_size: int) -> List[Tuple[Any, ...]]:
        """Return a random mini-batch of experiences."""
        if not self.buffer:
            return []
        return random.sample(self.buffer, min(batch_size, len(self.buffer)))

    def __len__(self) -> int:  # pragma: no cover - trivial
        return len(self.buffer)
