from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Dict, Optional

from .replay_buffer import ReplayBuffer
from .ewc import EWC
from .state_builder import StateBuilder


@dataclass
class PPOAgent:
    """Simplified PPO agent with actor-critic update and EWC."""

    state_builder: StateBuilder
    replay_buffer: ReplayBuffer
    ewc: Optional[EWC] = None
    gamma: float = 0.99
    value: Dict[str, float] = field(default_factory=dict)

    def select_action(self, state: Dict[str, float]) -> int:
        """Return an action. Random for placeholder implementation."""
        return random.choice([0, 1])

    def store_transition(
        self,
        state: Dict[str, float],
        action: int,
        reward: float,
        next_state: Dict[str, float],
        done: bool,
    ) -> None:
        self.replay_buffer.add((state, action, reward, next_state, done))

    def value_estimate(self, state: Dict[str, float]) -> float:
        return sum(state.get(k, 0.0) * self.value.get(k, 0.0) for k in state.keys())

    def update(self, batch_size: int = 4) -> None:
        batch = self.replay_buffer.sample(batch_size)
        if not batch:
            return

        penalty_grad = {}
        if self.ewc:
            for name in self.value.keys():
                penalty_grad[name] = (
                    2
                    * self.ewc.lambda_
                    * self.ewc.fisher.get(name, 0.0)
                    * (self.value.get(name, 0.0) - self.ewc.opt_params.get(name, 0.0))
                )

        for state, action, reward, next_state, done in batch:
            target = reward + self.gamma * self.value_estimate(next_state) * (1 - int(done))
            td_error = target - self.value_estimate(state)
            for k, v in state.items():
                update = 0.01 * td_error * v
                if self.ewc:
                    update -= penalty_grad.get(k, 0.0)
                self.value[k] = self.value.get(k, 0.0) + update

        self.replay_buffer.buffer.clear()

    def consolidate(self) -> None:
        if self.ewc:
            self.ewc.update_importance(self.value)

    # Integration with RLTrainer
    def train(self, metrics: Dict[str, float]) -> None:
        state = self.state_builder.build()
        reward = sum(metrics.get(k, 0.0) for k in metrics if isinstance(metrics[k], (int, float)))
        action = self.select_action(state)
        self.store_transition(state, action, reward, state, True)
        self.update()
