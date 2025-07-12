# RL Training Metrics

SelfArchitectAI training jobs expose Prometheus metrics when started with a non-zero `metrics_port`.

## Metrics

- `rl_training_reward` – reward for the most recent episode
- `rl_training_episode_length` – steps in the most recent episode
- `rl_training_reward_summary` – summary of reward values
- `rl_training_episode_length_summary` – summary of episode lengths
- `rl_training_episodes_total` – counter of processed episodes

## Dashboard Setup

1. Install Prometheus and Grafana as described in `docs/observability.md`.
2. Run a training job using `RLTrainer(metrics_port=<port>)` so the metrics endpoint is available.
3. Execute `python scripts/update_dashboards.py` to generate `grafana/dashboards/rl_metrics.json`.
4. Import this JSON file into Grafana and select your Prometheus data source.

The dashboard displays average reward and episode length over time along with the total episode count.
