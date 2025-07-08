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
        best_score = self.environment.evaluate(seed)
        for _ in range(self.generations):
            scores = [(self.environment.evaluate(g), g) for g in population]
            scores.sort(key=lambda x: x[0], reverse=True)
            best_score, best_gene = scores[0]
            population = [best_gene] + [best_gene.mutate() for _ in range(self.population_size - 1)]
            self.history.append(best_gene)
        return best_gene
