import json
from reflector.rl.reward import calculate_reward

from core.observability import MetricsProvider
from vision.vision_engine import RLAgent
from vision.training import RLTrainer
from vision.replay_buffer import ReplayBuffer


def test_rl_trainer_runs(tmp_path):
    metrics_file = tmp_path / "metrics.json"
    metrics_file.write_text('{"coverage": 85}')
    provider = MetricsProvider(metrics_file)
    agent = RLAgent()
    trainer = RLTrainer(agent=agent, metrics_provider=provider)
    trainer.run()
    assert agent.training_data == [{"coverage": 1.0}]


def test_rl_training_persists_data(tmp_path):
    metrics_file = tmp_path / "metrics.json"
    metrics_file.write_text('{"coverage": 99}')
    train_file = tmp_path / "train.log"
    provider = MetricsProvider(metrics_file)
    agent = RLAgent(training_path=train_file)
    trainer = RLTrainer(agent=agent, metrics_provider=provider)
    trainer.run()
    assert train_file.exists()
    data = train_file.read_text().strip()
    assert json.loads(data) == {"coverage": 1.0}


def test_rl_trainer_includes_log_metrics(tmp_path):
    metrics_file = tmp_path / "metrics.json"
    metrics_file.write_text('{"coverage": 2}')
    log_file = tmp_path / "train.log"
    log_file.write_text("error\nline\nline\nline\n")
    provider = MetricsProvider(metrics_file)
    agent = RLAgent()
    trainer = RLTrainer(agent=agent, metrics_provider=provider, logs_path=log_file)
    trainer.run()
    entry = agent.training_data[0]
    assert entry["log_lines"] == 1.0
    assert entry["error_lines"] == 0.25


def test_rl_trainer_consolidates(tmp_path):
    metrics_file = tmp_path / "metrics.json"
    metrics_file.write_text('{"coverage": 42}')

    provider = MetricsProvider(metrics_file)

    class DummyAgent(RLAgent):
        def __init__(self):
            super().__init__()
            self.calls = 0

        def consolidate(self):
            self.calls += 1

    agent = DummyAgent()
    trainer = RLTrainer(agent=agent, metrics_provider=provider)
    trainer.run(episodes=2)
    assert agent.calls == 2


def test_rl_trainer_records_replay_buffer(tmp_path):
    metrics_file = tmp_path / "m.json"
    metrics_file.write_text('{"coverage": 50}')
    provider = MetricsProvider(metrics_file)
    agent = RLAgent()
    buffer = ReplayBuffer(capacity=4)
    trainer = RLTrainer(agent=agent, metrics_provider=provider, replay_buffer=buffer)
    trainer.run(episodes=2)
    assert len(buffer) == 2
    state, reward = buffer.sample(1)[0]
    assert isinstance(state, dict)
    assert isinstance(reward, float)

def test_rl_agent_train_logs_and_terms(tmp_path):
    log_file = tmp_path / "log.json"
    agent = RLAgent(training_path=log_file)
    metrics = {"success": 1, "runtime": 5}
    expected_reward, terms = calculate_reward(metrics)
    reward = agent.train(metrics)
    assert reward == expected_reward
    assert agent.last_reward_terms == terms
    assert agent.training_data[0] == metrics
    assert json.loads(log_file.read_text().strip()) == metrics

