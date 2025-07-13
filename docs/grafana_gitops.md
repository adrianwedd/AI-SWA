# Grafana GitOps Workflow

Dashboards for AI-SWA are managed as code and deployed automatically.

1. Run `python scripts/update_dashboards.py` to generate JSON files under
   `grafana/dashboards/`. This directory is dedicated solely to dashboard
   definitions.
2. Commit the JSON files to version control. Any modification inside
   `grafana/dashboards/` triggers the `Grafana Deploy` workflow defined at
   `.github/workflows/grafana.yml`.
3. The workflow installs dependencies and runs `python scripts/apply_dashboards.py`
   to post each dashboard to the configured Grafana instance via its HTTP API.
4. Provide `GRAFANA_URL` and `GRAFANA_API_KEY` as repository secrets so the
 workflow can authenticate.

This approach keeps Grafana configuration fully declarative and reproducible.

## RL Training Dashboard

The training scripts expose Prometheus metrics `rl_training_reward` and
`rl_training_episode_length`. Running `RLTrainer` with a non-zero
`metrics_port` starts a metrics endpoint (default `9200`).

Generate the dashboard JSON and commit `grafana/dashboards/rl_training.json` to
visualize these values in Grafana.

## Code Quality Dashboard

`code_quality.json` tracks code complexity, maintainability index and test results.
These metrics can be exported to Prometheus by your CI pipeline or
quality tools. Commit the JSON file to publish updates through the
Grafana workflow.
