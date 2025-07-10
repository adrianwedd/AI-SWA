from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict
import math
import random

from .experience import ReplayBuffer


@dataclass
class PPOAgent:
    """Minimal PPO agent storing experiences in a replay buffer."""

    replay_buffer: ReplayBuffer
    gamma: float = 0.99
    learning_rate: float = 0.01
    policy: Dict[str, float] = field(default_factory=dict)

    def select_action(self, state: Dict[str, float]) -> tuple[int, float]:
        z = sum(state.get(k, 0.0) * self.policy.get(k, 0.0) for k in state)
        p = 1.0 / (1.0 + math.exp(-z))
        action = 1 if random.random() < p else 0
        log_prob = math.log(p if action == 1 else 1.0 - p + 1e-8)
        return action, log_prob

    def train_step(self, state: Dict[str, float], reward: float) -> None:
        action, log_prob = self.select_action(state)
        self.replay_buffer.add((state, action, reward, state, True, log_prob))
        batch = self.replay_buffer.sample(batch_size=4)
        if not batch:
            return
        for s, a, r, _ns, _done, _lp in batch:
            z = sum(s.get(k, 0.0) * self.policy.get(k, 0.0) for k in s)
            p = 1.0 / (1.0 + math.exp(-z))
            advantage = r - p
            for k, v in s.items():
                grad = (1 - p) * v if a == 1 else -p * v
                self.policy[k] = self.policy.get(k, 0.0) + self.learning_rate * advantage * grad
        self.replay_buffer.buffer.clear()
