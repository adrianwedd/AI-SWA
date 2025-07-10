from vision import (
    Gene,
    EvolutionaryPolicyOptimizer,
    SimulationEnvironment,
    TwoSpeedEngine,
    TwoSpeedTrainer,
    Scheduler,
)
from core.observability import MetricsProvider


def test_two_speed_trainer(tmp_path):
    metrics_file = tmp_path / "metrics.json"
    metrics_file.write_text('{"reward": 1}')
    provider = MetricsProvider(metrics_file)
    env = SimulationEnvironment(metrics_provider=provider, episodes=1)
    gene = Gene()
    optimizer = EvolutionaryPolicyOptimizer(environment=env, generations=1)
    agent = env.build_agent(gene)
    engine = TwoSpeedEngine(inner_agent=agent, outer_loop=optimizer, gene=gene)
    scheduler = Scheduler()
    trainer = TwoSpeedTrainer(engine=engine, inner_steps=2, scheduler=scheduler)
    trainer.run(cycles=1)
    assert isinstance(trainer.engine.gene, Gene)
