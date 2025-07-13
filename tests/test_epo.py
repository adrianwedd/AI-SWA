from vision.epo import Gene, EvolutionaryPolicyOptimizer, SimulationEnvironment, TwoSpeedEngine
from core.observability import MetricsProvider
from core.production_simulator import (
    ProductionSimulator,
    Service,
    SimulationMetricsProvider,
)


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


def test_environment_builds_agent_with_gene_params(tmp_path):
    metrics_file = tmp_path / "m.json"
    metrics_file.write_text('{"reward": 1}')
    provider = MetricsProvider(metrics_file)
    env = SimulationEnvironment(metrics_provider=provider, episodes=1)
    gene = Gene(architecture=(32,), learning_rate=0.005, clip_epsilon=0.3, gamma=0.9)
    agent = env.build_agent(gene)
    assert agent.learning_rate == gene.learning_rate
    assert agent.clip_epsilon == gene.clip_epsilon
    assert agent.gamma == gene.gamma


def test_environment_custom_buffer_and_strategy(tmp_path):
    metrics_file = tmp_path / "m.json"
    metrics_file.write_text('{"reward": 1}')
    provider = MetricsProvider(metrics_file)
    env = SimulationEnvironment(
        metrics_provider=provider, episodes=1, buffer_capacity=5, sample_strategy="fifo"
    )
    gene = Gene()
    agent = env.build_agent(gene)
    assert agent.replay_buffer.capacity == 5
    assert agent.replay_buffer.strategy == "fifo"


class CountingSimulator(ProductionSimulator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.steps = 0

    def step(self, action):
        self.steps += 1
        return super().step(action)


def test_environment_evaluate_uses_simulator_step(tmp_path):
    workload = tmp_path / "workload.json"
    workload.write_text('[{"service": "api"}]')
    sim = CountingSimulator(workload_path=workload)
    sim.add_service(Service(name="api", capacity=1))
    provider = SimulationMetricsProvider(sim)
    env = SimulationEnvironment(
        metrics_provider=provider, simulator=sim, episodes=1
    )
    gene = Gene()
    env.evaluate(gene)
    assert sim.steps >= 1
