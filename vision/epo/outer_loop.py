from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from .gene import Gene
from .simulation import SimulationEnvironment


@dataclass
class EvolutionaryPolicyOptimizer:
    """Simple evolutionary strategy to optimize agent genes."""

    environment: SimulationEnvironment
    population_size: int = 4
    generations: int = 1
    history: List[Gene] = field(default_factory=list)

    def evolve(self, seed: Gene) -> Gene:
        """Return the best evolved gene starting from ``seed``."""
        population = [seed] + [seed.mutate() for _ in range(self.population_size - 1)]
        best_gene = seed
        for _ in range(self.generations):
            scored = sorted(
                ((self.environment.evaluate(g), g) for g in population),
                key=lambda x: x[0],
                reverse=True,
            )
            best_gene = scored[0][1]
            self.history.append(best_gene)
            parents = [g for _, g in scored[:2]]
            population = parents + [parents[0].crossover(parents[1]).mutate() for _ in range(self.population_size - 2)]
        return best_gene
