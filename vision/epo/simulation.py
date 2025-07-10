from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

from core.production_simulator import ProductionSimulator

from core.observability import MetricsProvider
from reflector.rl.reward import calculate_reward
from ..ppo import ReplayBuffer, StateBuilder, PPOAgent
from .gene import Gene


@dataclass
class SimulationEnvironment:
    """High-fidelity offline environment for evaluating agents."""

    metrics_provider: MetricsProvider
    episodes: int = 3
    simulator: Optional[ProductionSimulator] = None

    def build_agent(self, gene: Gene) -> PPOAgent:
        """Instantiate a PPO agent using ``gene`` hyperparameters."""
        buffer = ReplayBuffer(capacity=gene.hidden_dim)
        builder = StateBuilder(self.metrics_provider)
        return PPOAgent(
            state_builder=builder,
            replay_buffer=buffer,
            gamma=gene.gamma,
            learning_rate=gene.learning_rate,
            clip_epsilon=gene.clip_epsilon,
        )

    def snapshot(self) -> Dict[str, object]:
        """Return environment snapshot if possible."""
        if self.simulator:
            return self.simulator.snapshot()
        if hasattr(self.metrics_provider, "snapshot"):
            return self.metrics_provider.snapshot()  # type: ignore[no-any-return]
        return {}

    def restore(self, state: Dict[str, object]) -> None:
        """Restore environment state from ``state``."""
        if self.simulator and state:
            self.simulator.restore(state)
        elif hasattr(self.metrics_provider, "restore"):
            self.metrics_provider.restore(state)

    def evaluate(self, gene: Gene) -> float:
        """Return cumulative reward for agent defined by ``gene``."""
        snapshot = self.snapshot()
        agent = self.build_agent(gene)
        total = 0.0
        for _ in range(self.episodes):
            metrics = self.metrics_provider.collect()
            agent.train(metrics)
            reward, _terms = calculate_reward(metrics)
            total += reward
        self.restore(snapshot)
        return total + sum(agent.value.values())
