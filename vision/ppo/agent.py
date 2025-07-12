from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Dict, Optional

from .replay_buffer import ReplayBuffer
from .ewc import EWC
from .state_builder import StateBuilder
from reflector.rl.reward import calculate_reward


@dataclass
class PPOAgent:
    """Simplified PPO agent with actor-critic update and EWC."""

    state_builder: StateBuilder
    replay_buffer: ReplayBuffer
    ewc: Optional[EWC] = None
    gamma: float = 0.99
    learning_rate: float = 0.01
    clip_epsilon: float = 0.2
    policy: Dict[str, float] = field(default_factory=dict)
    value: Dict[str, float] = field(default_factory=dict)
    last_batch: list = field(default_factory=list)

    def select_action(self, state: Dict[str, float]) -> tuple[int, float]:
        """Return an action and its log probability under the current policy."""
        z = sum(state.get(k, 0.0) * self.policy.get(k, 0.0) for k in state.keys())
        p = 1.0 / (1.0 + math.exp(-z))
        action = 1 if random.random() < p else 0
        log_prob = math.log(p if action == 1 else 1.0 - p + 1e-8)
        return action, log_prob

    def store_transition(
        self,
        state: Dict[str, float],
        action: int,
        reward: float,
        next_state: Dict[str, float],
        done: bool,
        log_prob: float,
    ) -> None:
        self.replay_buffer.add((state, action, reward, next_state, done, log_prob))

    def value_estimate(self, state: Dict[str, float]) -> float:
        return sum(state.get(k, 0.0) * self.value.get(k, 0.0) for k in state.keys())

    def update(self, batch_size: int = 4) -> None:
        batch = self.replay_buffer.sample(batch_size)
        if not batch:
            return
        self.last_batch = batch

        penalty_grad = {}
        actor_penalty = {}
        if self.ewc:
            params = {**self.policy, **self.value}
            for name in params.keys():
                penalty_grad[name] = (
                    2
                    * self.ewc.lambda_
                    * self.ewc.fisher.get(name, 0.0)
                    * (params.get(name, 0.0) - self.ewc.opt_params.get(name, 0.0))
                )
                actor_penalty[name] = penalty_grad[name] * 0.1

        for state, action, reward, next_state, done, old_log_prob in batch:
            v_next = self.value_estimate(next_state)
            v_curr = self.value_estimate(state)
            target = reward + self.gamma * v_next * (1 - int(done))
            advantage = target - v_curr

            z = sum(state.get(k, 0.0) * self.policy.get(k, 0.0) for k in state.keys())
            p = 1.0 / (1.0 + math.exp(-z))
            new_log_prob = math.log(p if action == 1 else 1.0 - p + 1e-8)
            ratio = math.exp(new_log_prob - old_log_prob)
            clipped = max(min(ratio, 1 + self.clip_epsilon), 1 - self.clip_epsilon)
            policy_factor = min(ratio, clipped) * advantage

            for k, v in state.items():
                if action == 1:
                    grad_log_prob = (1 - p) * v
                else:
                    grad_log_prob = -p * v
                update = self.learning_rate * policy_factor * grad_log_prob
                if self.ewc:
                    update -= actor_penalty.get(k, 0.0)
                self.policy[k] = self.policy.get(k, 0.0) + update

                val_update = self.learning_rate * advantage * v
                if self.ewc:
                    val_update -= penalty_grad.get(k, 0.0)
                    val_update *= 0.5
                self.value[k] = self.value.get(k, 0.0) + val_update

        self.replay_buffer.buffer.clear()

    def consolidate(self) -> None:
        if self.ewc:
            params = {**self.policy, **self.value}
            self.ewc.update_importance(params, batch=self.last_batch)

    # Integration with RLTrainer
    def train(self, metrics: Dict[str, float]) -> None:
        state = self.state_builder.build()
        reward, _terms = calculate_reward(metrics)
        action, log_prob = self.select_action(state)
        self.store_transition(state, action, reward, state, True, log_prob)
        self.update()
