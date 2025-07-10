from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional
import math
import random

from .experience import ReplayBuffer
from .ewc import EWC
from ..state_builder import StateBuilder
from .models.actor_network import ActorNetwork
from .models.critic_network import CriticNetwork
from .reward import calculate_reward
from .gen_actions import ActionGenerator


@dataclass
class PPOAgent:
    """Proximal Policy Optimization agent with lightweight networks."""

    replay_buffer: ReplayBuffer
    state_builder: StateBuilder
    actor: ActorNetwork = field(default_factory=ActorNetwork)
    critic: CriticNetwork = field(default_factory=CriticNetwork)
    ewc: Optional[EWC] = None
    gamma: float = 0.99
    clip_epsilon: float = 0.2
    action_gen: Optional[ActionGenerator] = None
    last_batch: list = field(default_factory=list)

    def __post_init__(self) -> None:  # expose weights for backward compatibility
        self.policy = self.actor.weights
        self.value = self.critic.weights

    def select_action(self, state: Dict[str, float]) -> tuple[int, float]:
        prob = self.actor.probability(state)
        action = 1 if random.random() < prob else 0
        log_prob = math.log(prob if action == 1 else 1.0 - prob + 1e-8)
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

    def update(self, batch_size: int = 4) -> None:
        batch = self.replay_buffer.sample(batch_size)
        if not batch:
            return
        self.last_batch = batch

        penalty_grad: Dict[str, float] = {}
        if self.ewc:
            for name in self.value.keys():
                penalty_grad[name] = (
                    2
                    * self.ewc.lambda_
                    * self.ewc.fisher.get(name, 0.0)
                    * (self.value.get(name, 0.0) - self.ewc.opt_params.get(name, 0.0))
                )

        for state, action, reward, next_state, done, old_log_prob in batch:
            v_next = self.critic.value(next_state)
            v_curr = self.critic.value(state)
            target = reward + self.gamma * v_next * (1 - int(done))
            advantage = target - v_curr

            self.actor.update(state, action, advantage, old_log_prob, self.clip_epsilon)

            for k, v in state.items():
                update = self.critic.learning_rate * (target - v_curr) * v
                if self.ewc:
                    update -= penalty_grad.get(k, 0.0)
                self.value[k] = self.value.get(k, 0.0) + update

        self.replay_buffer.buffer.clear()

    def consolidate(self) -> None:
        if self.ewc:
            self.ewc.update_importance(self.value, batch=self.last_batch)

    def train_step(self, metrics: Dict[str, float]) -> None:
        state = self.state_builder.build()
        reward, _terms = calculate_reward(metrics)
        action, log_prob = self.select_action(state)
        self.store_transition(state, action, reward, state, True, log_prob)
        self.update()

    # alias for compatibility with vision.ppo agent
    def train(self, metrics: Dict[str, float]) -> None:
        self.train_step(metrics)

    def propose_patch(
        self,
        context: str,
        max_tokens: int = 64,
        num_actions: int = 3,
        max_len: int = 200,
    ) -> str:
        """Return best ranked patch proposal for ``context``."""
        if not self.action_gen:
            return ""
        patches = self.action_gen.propose(
            context, max_tokens=max_tokens, num_actions=num_actions
        )
        patches = self.action_gen.filter_actions(patches, max_len=max_len)
        patches = self.action_gen.rank_actions(patches)
        return patches[0] if patches else ""
