from vision.epo import Gene, EvolutionaryPolicyOptimizer, SimulationEnvironment, TwoSpeedEngine
from core.observability import MetricsProvider


def test_gene_mutation_and_crossover():
    g1 = Gene()
    g2 = g1.mutate()
    g3 = g1.crossover(g2)
    assert g1 != g2
    assert isinstance(g3, Gene)


def test_evolutionary_policy_optimizer(tmp_path):
    metrics_file = tmp_path / "m.json"
    metrics_file.write_text('{"score": 1}')
    provider = MetricsProvider(metrics_file)
    env = SimulationEnvironment(metrics_provider=provider, episodes=1)
    epo = EvolutionaryPolicyOptimizer(environment=env, generations=1)
    best = epo.evolve(Gene())
    assert isinstance(best, Gene)
    assert epo.history


def test_two_speed_engine(tmp_path):
    metrics_file = tmp_path / "m.json"
    metrics_file.write_text('{"reward": 1}')
    provider = MetricsProvider(metrics_file)
    env = SimulationEnvironment(metrics_provider=provider, episodes=1)
    gene = Gene()
    optimizer = EvolutionaryPolicyOptimizer(environment=env, generations=1)
    agent = env.build_agent(gene)
    engine = TwoSpeedEngine(inner_agent=agent, outer_loop=optimizer, gene=gene)
    engine.inner_step()
    engine.outer_cycle()
    assert isinstance(engine.gene, Gene)
