from vision import (
    Gene,
    EvolutionaryPolicyOptimizer,
    SimulationEnvironment,
    TwoSpeedEngine,
    TwoSpeedTrainer,
)
from core.observability import MetricsProvider


class DummyEnv(SimulationEnvironment):
    """Environment that scores genes by learning rate."""

    def evaluate(self, gene: Gene) -> float:
        return gene.learning_rate


def test_two_speed_improves_over_ppo(tmp_path):
    metrics_file = tmp_path / "m.json"
    metrics_file.write_text("{}")
    provider = MetricsProvider(metrics_file)
    env = DummyEnv(metrics_provider=provider, episodes=1)
    seed = Gene(learning_rate=0.01)
    baseline_score = env.evaluate(seed)
    optimizer = EvolutionaryPolicyOptimizer(environment=env, generations=1)
    agent = env.build_agent(seed)
    engine = TwoSpeedEngine(inner_agent=agent, outer_loop=optimizer, gene=seed)
    trainer = TwoSpeedTrainer(engine=engine, inner_steps=1)
    trainer.run(cycles=1)
    new_score = env.evaluate(trainer.engine.gene)
    assert new_score > baseline_score
