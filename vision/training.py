from __future__ import annotations

"""Simple RL training pipeline for the Vision Engine."""

from dataclasses import dataclass, field

from prometheus_client import Gauge, start_http_server

from core.observability import MetricsProvider
from .vision_engine import RLAgent

REWARD_GAUGE = Gauge("rl_training_reward", "Reward for the last episode")
LENGTH_GAUGE = Gauge("rl_training_episode_length", "Steps in the last episode")


@dataclass
class RLTrainer:
    """Train an :class:`RLAgent` using observability metrics."""

    agent: RLAgent
    metrics_provider: MetricsProvider
    metrics_port: int = 0
    _server_started: bool = field(default=False, init=False, repr=False)

    def run(self, episodes: int = 1) -> None:
        """Collect metrics and pass them to the agent's training routine."""
        if self.metrics_port and not self._server_started:
            start_http_server(self.metrics_port)
            self._server_started = True
        for _ in range(episodes):
            metrics = self.metrics_provider.collect()
            reward = self.agent.train(metrics)
            if hasattr(self.agent, "consolidate"):
                try:
                    self.agent.consolidate()
                except Exception:  # pragma: no cover - safeguard
                    pass
            REWARD_GAUGE.set(reward)
            LENGTH_GAUGE.set(len(metrics))
