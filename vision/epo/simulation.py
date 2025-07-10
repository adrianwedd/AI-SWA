from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from core.observability import MetricsProvider
from core.reward import calculate_reward
from ..ppo import ReplayBuffer, StateBuilder, PPOAgent
from .gene import Gene


@dataclass
class SimulationEnvironment:
    """High-fidelity offline environment for evaluating agents."""

    metrics_provider: MetricsProvider
    episodes: int = 3

    def build_agent(self, gene: Gene) -> PPOAgent:
        """Instantiate a PPO agent using ``gene`` hyperparameters."""
        buffer = ReplayBuffer(capacity=gene.hidden_dim)
        builder = StateBuilder(self.metrics_provider)
        return PPOAgent(state_builder=builder, replay_buffer=buffer, gamma=0.99)

    def evaluate(self, gene: Gene) -> float:
        """Return cumulative reward for agent defined by ``gene``."""
        agent = self.build_agent(gene)
        total = 0.0
        for _ in range(self.episodes):
            metrics = self.metrics_provider.collect()
            agent.train(metrics)
            total += calculate_reward(metrics)
        return total + sum(agent.value.values())
