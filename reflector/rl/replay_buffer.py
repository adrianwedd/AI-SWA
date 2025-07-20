from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List, Tuple, Optional
from pathlib import Path
import json
import random


@dataclass
class ReplayBuffer:
    """Fixed-size experience replay buffer with optional persistence."""

    capacity: int
    strategy: str = "uniform"
    path: Optional[Path] = None
    autosave: bool = True
    buffer: List[Tuple[Any, ...]] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.path:
            self.load()

    def add(self, transition: Tuple[Any, ...]) -> None:
        """Store ``transition`` and evict oldest when over capacity."""
        if len(self.buffer) >= self.capacity:
            self.buffer.pop(0)
        self.buffer.append(transition)
        if self.autosave:
            self.save()

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

    def load(self) -> None:
        """Load persisted transitions from ``path`` if available."""
        if not self.path or not self.path.exists():
            return
        try:
            with self.path.open("r", encoding="utf-8") as fh:
                self.buffer = json.load(fh)
        except Exception:  # pragma: no cover - IO errors
            self.buffer = []

    def save(self) -> None:
        """Persist buffered transitions to ``path``."""
        if not self.path:
            return
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("w", encoding="utf-8") as fh:
                json.dump(self.buffer, fh)
        except Exception:  # pragma: no cover - IO errors
            pass
