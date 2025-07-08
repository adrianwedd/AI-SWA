from __future__ import annotations

from dataclasses import dataclass

from ..ppo import PPOAgent
from .gene import Gene
from .outer_loop import EvolutionaryPolicyOptimizer


@dataclass
class TwoSpeedEngine:
    """Connect inner PPO agent with outer evolutionary optimizer."""

    inner_agent: PPOAgent
    outer_loop: EvolutionaryPolicyOptimizer
    gene: Gene

    def inner_step(self) -> None:
        """Run a single PPO training step using environment metrics."""
        metrics = self.outer_loop.environment.metrics_provider.collect()
        self.inner_agent.train(metrics)

    def outer_cycle(self) -> None:
        """Evolve the gene and refresh the inner agent."""
        self.gene = self.outer_loop.evolve(self.gene)
        self.inner_agent = self.outer_loop.environment.build_agent(self.gene)
