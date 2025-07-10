from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional

from ..state_builder import StateBuilder
from .reward import calculate_reward
from .gen_actions import ActionGenerator
import math
import random

from .experience import ReplayBuffer
from .ewc import EWC


@dataclass
class PPOAgent:
    """Minimal PPO agent storing experiences in a replay buffer."""

    replay_buffer: ReplayBuffer
    state_builder: StateBuilder
    ewc: Optional[EWC] = None
    gamma: float = 0.99
    learning_rate: float = 0.01
    action_gen: Optional[ActionGenerator] = None
    policy: Dict[str, float] = field(default_factory=dict)

    def select_action(self, state: Dict[str, float]) -> tuple[int, float]:
        z = sum(state.get(k, 0.0) * self.policy.get(k, 0.0) for k in state)
        p = 1.0 / (1.0 + math.exp(-z))
        action = 1 if random.random() < p else 0
        log_prob = math.log(p if action == 1 else 1.0 - p + 1e-8)
        return action, log_prob

    def train_step(self, metrics: Dict[str, float]) -> None:
        """Update policy using ``metrics`` and the current state."""
        state = self.state_builder.build()
        reward, _terms = calculate_reward(metrics)
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

    def consolidate(self) -> None:
        if self.ewc:
            self.ewc.update_importance(self.policy)

    def propose_patch(self, context: str, max_tokens: int = 64) -> str:
        """Return a code patch proposal generated from ``context``."""
        if not self.action_gen:
            return ""
        patches = self.action_gen.propose(context, max_tokens=max_tokens)
        return patches[0] if patches else ""
