from __future__ import annotations

from dataclasses import dataclass, field
import json
import random
from pathlib import Path
from typing import List

from .experience import ReplayBuffer
from .ppo_agent import PPOAgent
from .models.actor_network import ActorNetwork
from .models.critic_network import CriticNetwork
from ..state_builder import StateBuilder
from .reward import calculate_reward
from core.observability import MetricsProvider


@dataclass
class HyperParams:
    """PPO hyperparameters subject to evolution."""

    buffer_capacity: int = 8
    sample_strategy: str = "uniform"
    actor_lr: float = 0.01
    critic_lr: float = 0.01
    gamma: float = 0.99
    clip_epsilon: float = 0.2

    def mutate(self) -> HyperParams:
        """Return a slightly modified copy of these params."""
        return HyperParams(
            buffer_capacity=max(2, self.buffer_capacity + random.randint(-2, 2)),
            actor_lr=max(1e-5, self.actor_lr * random.uniform(0.8, 1.2)),
            critic_lr=max(1e-5, self.critic_lr * random.uniform(0.8, 1.2)),
            gamma=min(0.999, max(0.5, self.gamma + random.uniform(-0.05, 0.05))),
            clip_epsilon=min(1.0, max(0.05, self.clip_epsilon + random.uniform(-0.05, 0.05))),
            sample_strategy=self.sample_strategy,
        )

    def crossover(self, other: HyperParams) -> HyperParams:
        """Combine attributes from this and ``other``."""
        return HyperParams(
            buffer_capacity=random.choice([self.buffer_capacity, other.buffer_capacity]),
            actor_lr=random.choice([self.actor_lr, other.actor_lr]),
            critic_lr=random.choice([self.critic_lr, other.critic_lr]),
            gamma=random.choice([self.gamma, other.gamma]),
            clip_epsilon=random.choice([self.clip_epsilon, other.clip_epsilon]),
            sample_strategy=random.choice([self.sample_strategy, other.sample_strategy]),
        )

    def to_dict(self) -> dict:
        return {
            "buffer_capacity": self.buffer_capacity,
            "actor_lr": self.actor_lr,
            "critic_lr": self.critic_lr,
            "gamma": self.gamma,
            "clip_epsilon": self.clip_epsilon,
            "sample_strategy": self.sample_strategy,
        }


@dataclass
class EvolutionEnvironment:
    """Offline environment for evaluating hyperparameters."""

    metrics_provider: MetricsProvider
    episodes: int = 3

    def build_agent(self, params: HyperParams) -> PPOAgent:
        buffer = ReplayBuffer(
            capacity=params.buffer_capacity, strategy=params.sample_strategy
        )
        builder = StateBuilder(self.metrics_provider)
        actor = ActorNetwork(learning_rate=params.actor_lr)
        critic = CriticNetwork(learning_rate=params.critic_lr)
        return PPOAgent(
            replay_buffer=buffer,
            state_builder=builder,
            actor=actor,
            critic=critic,
            gamma=params.gamma,
            clip_epsilon=params.clip_epsilon,
        )

    def evaluate(self, params: HyperParams) -> float:
        agent = self.build_agent(params)
        total = 0.0
        for _ in range(self.episodes):
            metrics = self.metrics_provider.collect()
            agent.train_step(metrics)
            reward, _ = calculate_reward(metrics)
            total += reward
        return total + sum(agent.value.values())


@dataclass
class HyperParamEvolution:
    """Run evolutionary cycles to optimize PPO hyperparameters."""

    environment: EvolutionEnvironment
    population_size: int = 4
    generations: int = 1
    results_path: Path = Path("best_configs.json")
    history: List[HyperParams] = field(default_factory=list)

    def evolve(self, seed: HyperParams) -> HyperParams:
        """Return the best evolved parameters starting from ``seed``."""
        population = [seed] + [seed.mutate() for _ in range(self.population_size - 1)]
        best = seed
        best_score = self.environment.evaluate(seed)
        for _ in range(self.generations):
            scored = sorted(
                ((self.environment.evaluate(g), g) for g in population),
                key=lambda x: x[0],
                reverse=True,
            )
            best_score, best = scored[0]
            self.history.append(best)
            parents = [g for _, g in scored[:2]]
            population = parents + [parents[0].crossover(parents[1]).mutate() for _ in range(self.population_size - 2)]
        self._persist(best, best_score)
        return best

    def run(self, seed: HyperParams, cycles: int = 1) -> HyperParams:
        """Iteratively evolve ``seed`` for ``cycles`` generations."""
        best = seed
        for _ in range(cycles):
            best = self.evolve(best)
        return best

    def _persist(self, params: HyperParams, score: float) -> None:
        results: List[dict] = []
        if self.results_path.exists():
            try:
                with self.results_path.open("r", encoding="utf-8") as f:
                    results = json.load(f)
            except Exception:
                results = []
        results.append({"score": score, "params": params.to_dict()})
        results = sorted(results, key=lambda x: x["score"], reverse=True)[:5]
        with self.results_path.open("w", encoding="utf-8") as f:
            json.dump(results, f)


__all__ = [
    "HyperParams",
    "EvolutionEnvironment",
    "HyperParamEvolution",
]
