from core.observability import MetricsProvider
from reflector.rl.evolution import HyperParams, EvolutionEnvironment, EvolutionStrategyOptimizer


def test_es_optimizer(tmp_path):
    metrics_file = tmp_path / "metrics.json"
    metrics_file.write_text('{"reward": 1}')
    provider = MetricsProvider(metrics_file)
    env = EvolutionEnvironment(metrics_provider=provider, episodes=1)
    es = EvolutionStrategyOptimizer(environment=env, generations=1)
    best = es.evolve(HyperParams())
    assert isinstance(best, HyperParams)
    assert es.history

