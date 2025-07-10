from core.observability import MetricsProvider
from reflector.rl.evolution import (
    HyperParams,
    EvolutionEnvironment,
    HyperParamEvolution,
)


def test_hyperparams_mutation_and_crossover():
    p1 = HyperParams()
    p2 = p1.mutate()
    p3 = p1.crossover(p2)
    assert p1 != p2
    assert isinstance(p3, HyperParams)


def test_hyperparam_evolution(tmp_path):
    metrics_file = tmp_path / "metrics.json"
    metrics_file.write_text('{"reward": 1}')
    provider = MetricsProvider(metrics_file)
    env = EvolutionEnvironment(metrics_provider=provider, episodes=1)
    evo = HyperParamEvolution(environment=env, generations=1, results_path=tmp_path / "best.json")
    best = evo.run(HyperParams(), cycles=1)
    assert isinstance(best, HyperParams)
    assert evo.history
    assert (tmp_path / "best.json").exists()
