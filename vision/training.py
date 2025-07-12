from __future__ import annotations

"""Simple RL training pipeline for the Vision Engine."""

from dataclasses import dataclass, field
from typing import Optional, Dict

from pathlib import Path

from prometheus_client import Gauge, Counter, Summary, start_http_server

from core.observability import MetricsProvider
from .vision_engine import RLAgent
from .epo import TwoSpeedEngine, Scheduler
from .ppo import StateBuilder
from .replay_buffer import ReplayBuffer

REWARD_GAUGE = Gauge("rl_training_reward", "Reward for the last episode")
REWARD_SUMMARY = Summary(
    "rl_training_reward_summary", "Distribution of episode rewards"
)
LENGTH_GAUGE = Gauge("rl_training_episode_length", "Steps in the last episode")
LENGTH_SUMMARY = Summary(
    "rl_training_episode_length_summary", "Distribution of episode lengths"
)
EPISODES_COUNTER = Counter(
    "rl_training_episodes_total", "Total number of training episodes"
)
CORRECTNESS_GAUGE = Gauge(
    "rl_training_correctness", "Correctness component of the reward"
)
PERFORMANCE_GAUGE = Gauge(
    "rl_training_performance", "Performance component of the reward"
)
STYLE_GAUGE = Gauge("rl_training_style", "Style component of the reward")


@dataclass
class RLTrainer:
    """Train an :class:`RLAgent` using observability metrics."""

    agent: RLAgent
    metrics_provider: MetricsProvider
    replay_buffer: Optional[ReplayBuffer] = None
    logs_path: Optional[Path] = None
    metrics_port: int = 0
    _server_started: bool = field(default=False, init=False, repr=False)
    _state_builder: Optional[StateBuilder] = field(default=None, init=False, repr=False)

    def run(self, episodes: int = 1) -> None:
        """Collect metrics and pass them to the agent's training routine."""
        if self.metrics_port and not self._server_started:
            start_http_server(self.metrics_port)
            self._server_started = True
        if not self._state_builder:
            self._state_builder = StateBuilder(
                self.metrics_provider, logs_path=self.logs_path
            )
        for _ in range(episodes):
            state: Dict[str, float] = self._state_builder.build()
            reward = self.agent.train(state)
            if self.replay_buffer is not None:
                self.replay_buffer.add((state, reward))
            if hasattr(self.agent, "consolidate"):
                try:
                    self.agent.consolidate()
                except Exception:  # pragma: no cover - safeguard
                    pass
            REWARD_GAUGE.set(reward)
            REWARD_SUMMARY.observe(reward)
            LENGTH_GAUGE.set(len(state))
            LENGTH_SUMMARY.observe(len(state))
            EPISODES_COUNTER.inc()
            terms = getattr(self.agent, "last_reward_terms", {})
            CORRECTNESS_GAUGE.set(terms.get("correctness", 0.0))
            PERFORMANCE_GAUGE.set(terms.get("performance", 0.0))
            STYLE_GAUGE.set(terms.get("style", 0.0))


@dataclass
class TwoSpeedTrainer:
    """Coordinate PPO inner loop and evolutionary outer loop."""

    engine: TwoSpeedEngine
    inner_steps: int = 1
    scheduler: Optional[Scheduler] = None

    def run(self, cycles: int = 1) -> None:
        """Run ``inner_steps`` and then an outer-loop cycle for each iteration."""
        for _ in range(cycles):
            for _ in range(self.inner_steps):
                if self.scheduler:
                    self.scheduler.schedule(self.engine.inner_step)
                else:
                    self.engine.inner_step()
            if self.scheduler:
                self.scheduler.schedule(self.engine.outer_cycle)
                self.scheduler.run()
            else:
                self.engine.outer_cycle()
