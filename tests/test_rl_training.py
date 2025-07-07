import json

from core.observability import MetricsProvider
from vision.vision_engine import RLAgent
from vision.training import RLTrainer


def test_rl_trainer_runs(tmp_path):
    metrics_file = tmp_path / "metrics.json"
    metrics_file.write_text('{"coverage": 85}')
    provider = MetricsProvider(metrics_file)
    agent = RLAgent()
    trainer = RLTrainer(agent=agent, metrics_provider=provider)
    trainer.run()
    assert agent.training_data == [{"coverage": 85}]


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
    assert json.loads(data) == {"coverage": 99}
