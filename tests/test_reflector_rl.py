from typing import Dict

import json
import random

from reflector.rl import ReplayBuffer, PPOAgent, EWC
from reflector.rl.training import HistoricalMetricsLoader, PPOAgent as SimpleAgent
from reflector import StateBuilder
from core.observability import MetricsProvider


def test_replay_buffer_add_and_sample():
    buf = ReplayBuffer(capacity=2)
    buf.add((1, 2))
    buf.add((2, 3))
    buf.add((3, 4))
    assert len(buf) == 2
    sample = buf.sample(1)
    assert len(sample) == 1
    assert sample[0] in [(2, 3), (3, 4)]

    fifo = ReplayBuffer(capacity=3, strategy="fifo")
    fifo.add((1, 2))
    fifo.add((2, 3))
    fifo.add((3, 4))
    fifo.add((4, 5))
    assert fifo.sample(2) == [(3, 4), (4, 5)]


def test_ppo_agent_updates_policy_and_clears_buffer(tmp_path):
    random.seed(0)
    metrics_file = tmp_path / "m.json"
    metrics_file.write_text('{"cpu": 0.1, "memory": 0.2, "error_rate": 0.0, "success": 1}')
    provider = MetricsProvider(metrics_file)
    builder = StateBuilder(provider)
    buf = ReplayBuffer(capacity=4)
    agent = PPOAgent(replay_buffer=buf, state_builder=builder)
    metrics = provider.collect()
    agent.train_step(metrics)
    assert len(buf) == 0
    assert agent.policy
    assert agent.value


def _train(agent: PPOAgent, metrics: Dict[str, float], steps: int = 5) -> None:
    for _ in range(steps):
        agent.train_step(metrics)


def test_ewc_reduces_catastrophic_forgetting(tmp_path):
    random.seed(0)
    metrics_file = tmp_path / "m.json"
    metrics_file.write_text('{"cpu": 0.1, "memory": 0.2, "error_rate": 0.0, "success": 1, "runtime": 1}')
    provider = MetricsProvider(metrics_file)
    builder = StateBuilder(provider)
    # Agent without EWC
    buf1 = ReplayBuffer(capacity=10)
    agent_no_ewc = PPOAgent(replay_buffer=buf1, state_builder=builder)
    pos_metrics = provider.collect()
    _train(agent_no_ewc, pos_metrics)
    weight_a = agent_no_ewc.policy.get("cpu", 0.0)
    metrics_file.write_text('{"cpu": 0.1, "memory": 0.2, "error_rate": 0.0, "success": 0, "runtime": 1}')
    neg_metrics = provider.collect()
    _train(agent_no_ewc, neg_metrics)
    weight_b = agent_no_ewc.policy.get("cpu", 0.0)
    forgetting_without = abs(weight_b - weight_a)

    # Agent with EWC
    buf2 = ReplayBuffer(capacity=10)
    ewc = EWC()
    agent_ewc = PPOAgent(replay_buffer=buf2, state_builder=builder, ewc=ewc)
    metrics_file.write_text('{"cpu": 0.1, "memory": 0.2, "error_rate": 0.0, "success": 1, "runtime": 1}')
    pos_metrics = provider.collect()
    _train(agent_ewc, pos_metrics)
    agent_ewc.consolidate()
    weight_a_ewc = agent_ewc.policy.get("cpu", 0.0)
    metrics_file.write_text('{"cpu": 0.1, "memory": 0.2, "error_rate": 0.0, "success": 0, "runtime": 1}')
    neg_metrics = provider.collect()
    _train(agent_ewc, neg_metrics)
    weight_b_ewc = agent_ewc.policy.get("cpu", 0.0)
    forgetting_with = abs(weight_b_ewc - weight_a_ewc)

    assert forgetting_with < forgetting_without


def test_train_step_samples_recent_experiences(tmp_path):
    random.seed(0)
    metrics_file = tmp_path / "m.json"
    metrics_file.write_text('{"reward": 1}')
    provider = MetricsProvider(metrics_file)
    builder = StateBuilder(provider)
    buf = ReplayBuffer(capacity=8)
    agent = PPOAgent(replay_buffer=buf, state_builder=builder)
    metrics = provider.collect()
    for _ in range(6):
        agent.train_step(metrics)
    # last_batch should contain at most 4 transitions sampled from the buffer
    assert agent.last_batch
    assert len(agent.last_batch) <= 4


def test_history_loader_with_ewc(tmp_path):
    random.seed(0)
    hist = tmp_path / "history.jsonl"
    pos = {"cpu": 0.1, "memory": 0.2, "error_rate": 0.0, "success": 1, "runtime": 1}
    hist.write_text(json.dumps(pos) + "\n")
    loader = HistoricalMetricsLoader(path=hist, sample_interval=1)

    metrics_file = tmp_path / "m.json"
    metrics_file.write_text(json.dumps(pos))
    provider = MetricsProvider(metrics_file)
    builder = StateBuilder(provider)

    buf1 = ReplayBuffer(capacity=10)
    agent_no_ewc = SimpleAgent(
        replay_buffer=buf1, state_builder=builder, history_loader=loader
    )
    for _ in range(3):
        agent_no_ewc.train_step(provider.collect())
    weight_a = agent_no_ewc.policy.get("cpu", 0.0)

    metrics_file.write_text(
        '{"cpu": 0.1, "memory": 0.2, "error_rate": 0.0, "success": 0, "runtime": 1}'
    )
    for _ in range(3):
        agent_no_ewc.train_step(provider.collect())
    weight_b = agent_no_ewc.policy.get("cpu", 0.0)
    forgetting_without = abs(weight_b - weight_a)

    loader2 = HistoricalMetricsLoader(path=hist, sample_interval=1)
    buf2 = ReplayBuffer(capacity=10)
    ewc = EWC()
    agent_ewc = SimpleAgent(
        replay_buffer=buf2, state_builder=builder, ewc=ewc, history_loader=loader2
    )
    metrics_file.write_text(json.dumps(pos))
    for _ in range(3):
        agent_ewc.train_step(provider.collect())
    agent_ewc.consolidate()
    weight_a_ewc = agent_ewc.policy.get("cpu", 0.0)
    metrics_file.write_text(
        '{"cpu": 0.1, "memory": 0.2, "error_rate": 0.0, "success": 0, "runtime": 1}'
    )
    for _ in range(3):
        agent_ewc.train_step(provider.collect())
    weight_b_ewc = agent_ewc.policy.get("cpu", 0.0)
    forgetting_with = abs(weight_b_ewc - weight_a_ewc)

    assert forgetting_with < forgetting_without
