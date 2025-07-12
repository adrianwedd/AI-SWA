from core.observability import MetricsProvider
import random
from reflector.rl.evolution import (
    HyperParams,
    EvolutionEnvironment,
    EvolutionStrategyOptimizer,
    PeriodicHyperParamMutation,
)


def test_es_optimizer(tmp_path):
    metrics_file = tmp_path / "metrics.json"
    metrics_file.write_text('{"reward": 1}')
    provider = MetricsProvider(metrics_file)
    env = EvolutionEnvironment(metrics_provider=provider, episodes=1)
    es = EvolutionStrategyOptimizer(environment=env, generations=1)
    best = es.evolve(HyperParams())
    assert isinstance(best, HyperParams)
    assert es.history


def test_periodic_mutation(tmp_path):
    metrics_file = tmp_path / "metrics.json"
    metrics_file.write_text("{}")
    provider = MetricsProvider(metrics_file)

    class DummyEnv(EvolutionEnvironment):
        def evaluate(self, params: HyperParams) -> float:
            return params.actor_lr

    env = DummyEnv(metrics_provider=provider, episodes=1)
    optimizer = EvolutionStrategyOptimizer(environment=env, generations=1)
    scheduler = PeriodicHyperParamMutation(optimizer=optimizer, period=2)
    random.seed(0)
    first = scheduler.params
    scheduler.step()
    second = scheduler.step()
    assert scheduler.params != first
    assert second == scheduler.params

