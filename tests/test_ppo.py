from core.observability import MetricsProvider
from vision.ppo import ReplayBuffer, EWC, StateBuilder, PPOAgent


def test_replay_buffer_add_and_sample():
    buf = ReplayBuffer(capacity=2)
    buf.add((1, 2, 3, 4, False))
    buf.add((2, 3, 4, 5, True))
    buf.add((3, 4, 5, 6, True))
    assert len(buf) == 2
    assert len(buf.sample(1)) == 1


def test_state_builder_numeric_filter(tmp_path):
    metrics_file = tmp_path / "m.json"
    metrics_file.write_text('{"coverage": 95, "note": "hi"}')
    provider = MetricsProvider(metrics_file)
    builder = StateBuilder(provider)
    state = builder.build()
    assert state == {"coverage": 95.0}


def test_state_builder_vector(tmp_path):
    metrics_file = tmp_path / "m.json"
    metrics_file.write_text('{"b": 2, "a": 1}')
    provider = MetricsProvider(metrics_file)
    builder = StateBuilder(provider)
    assert builder.vector() == [1.0, 2.0]


def test_ppo_agent_training_step(tmp_path):
    metrics_file = tmp_path / "m.json"
    metrics_file.write_text('{"reward": 1}')
    provider = MetricsProvider(metrics_file)
    builder = StateBuilder(provider)
    buffer = ReplayBuffer(capacity=4)
    ewc = EWC()
    agent = PPOAgent(state_builder=builder, replay_buffer=buffer, ewc=ewc)
    metrics = provider.collect()
    agent.train(metrics)
    assert len(buffer) == 0
    assert agent.value  # weights updated


def test_ppo_consolidation_updates_fisher(tmp_path):
    metrics_file = tmp_path / "m.json"
    metrics_file.write_text('{"reward": 2}')
    provider = MetricsProvider(metrics_file)
    builder = StateBuilder(provider)
    buffer = ReplayBuffer(capacity=4)
    ewc = EWC()
    agent = PPOAgent(state_builder=builder, replay_buffer=buffer, ewc=ewc)
    metrics = provider.collect()
    agent.train(metrics)
    agent.consolidate()
    assert ewc.opt_params == agent.value
    assert ewc.fisher
