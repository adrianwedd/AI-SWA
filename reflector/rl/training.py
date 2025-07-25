from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional, List

import json
from pathlib import Path

from ..state_builder import StateBuilder
from .reward import calculate_reward
from .gen_actions import ActionGenerator
import math
import random

from .replay_buffer import ReplayBuffer
from .ewc import EWC


@dataclass
class HistoricalMetricsLoader:
    """Load and sample metrics from a historical commit dataset."""

    path: Path
    sample_interval: int = 10
    data: List[Dict[str, float]] = field(default_factory=list)
    _counter: int = field(default=0, init=False, repr=False)

    def load(self) -> None:
        if not self.path.exists():
            self.data = []
            return
        try:
            with self.path.open("r", encoding="utf-8") as fh:
                self.data = [json.loads(line) for line in fh if line.strip()]
        except Exception:  # pragma: no cover - IO errors
            self.data = []

    def sample(self, batch_size: int) -> List[Dict[str, float]]:
        self._counter += 1
        if self._counter % self.sample_interval != 0:
            return []
        if not self.data:
            self.load()
        if not self.data:
            return []
        n = min(batch_size, len(self.data))
        return random.sample(self.data, n)


@dataclass
class PPOAgent:
    """Minimal PPO agent storing experiences in a replay buffer."""

    replay_buffer: ReplayBuffer
    state_builder: StateBuilder
    ewc: Optional[EWC] = None
    gamma: float = 0.99
    learning_rate: float = 0.01
    update_batch_size: int = 4
    action_gen: Optional[ActionGenerator] = None
    history_loader: Optional[HistoricalMetricsLoader] = None
    policy: Dict[str, float] = field(default_factory=dict)
    last_batch: list = field(default_factory=list)

    def __post_init__(self) -> None:
        if hasattr(self.replay_buffer, "load"):
            self.replay_buffer.load()
        if self.history_loader is not None:
            self.history_loader.load()

    def select_action(self, state: Dict[str, float]) -> tuple[int, float]:
        z = sum(state.get(k, 0.0) * self.policy.get(k, 0.0) for k in state)
        p = 1.0 / (1.0 + math.exp(-z))
        action = 1 if random.random() < p else 0
        log_prob = math.log(p if action == 1 else 1.0 - p + 1e-8)
        return action, log_prob

    def _update_from_state(
        self, state: Dict[str, float], metrics: Dict[str, float]
    ) -> None:
        reward, _terms = calculate_reward(metrics)
        action, log_prob = self.select_action(state)
        self.replay_buffer.add((state, action, reward, state, True, log_prob))
        batch = self.replay_buffer.sample(batch_size=self.update_batch_size)
        if not batch:
            return
        self.last_batch = batch
        for s, a, r, _ns, _done, _lp in batch:
            z = sum(s.get(k, 0.0) * self.policy.get(k, 0.0) for k in s)
            p = 1.0 / (1.0 + math.exp(-z))
            advantage = r - p
            for k, v in s.items():
                grad = (1 - p) * v if a == 1 else -p * v
                update = self.learning_rate * advantage * grad
                if self.ewc:
                    penalty = (
                        2
                        * self.ewc.lambda_
                        * self.ewc.fisher.get(k, 0.0)
                        * (self.policy.get(k, 0.0) - self.ewc.opt_params.get(k, 0.0))
                    )
                    update -= self.learning_rate * penalty
                self.policy[k] = self.policy.get(k, 0.0) + update
        self.replay_buffer.buffer.clear()

    def train_step(self, metrics: Dict[str, float]) -> None:
        """Update policy using ``metrics`` and the current state."""
        state = self.state_builder.build()
        self._update_from_state(state, metrics)
        if self.history_loader:
            for hist in self.history_loader.sample(self.update_batch_size):
                hist_state = {
                    k: float(v)
                    for k, v in hist.items()
                    if isinstance(v, (int, float))
                }
                self._update_from_state(hist_state, hist)
            if self.ewc:
                self.consolidate()

    def consolidate(self) -> None:
        if self.ewc:
            self.ewc.update_importance(self.policy, batch=self.last_batch)

    def propose_patch(self, context: str, max_tokens: int = 64) -> str:
        """Return a code patch proposal generated from ``context``."""
        if not self.action_gen:
            return ""
        patches = self.action_gen.propose(context, max_tokens=max_tokens)
        return patches[0] if patches else ""
