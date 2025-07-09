# Observability Setup

SelfArchitectAI services expose Prometheus metrics for local debugging. Two Grafana dashboards are provided and the stack now includes an OpenTelemetry Collector that receives OTLP data from each service and exports it for Prometheus scraping over TLS.

- **improvement-dashboard.json** – tracks task throughput.
- **observer-dashboard.json** – monitors worker CPU, memory and aggregate task metrics.

## Usage

1. Run `observability/generate_certs.sh` once to create self‑signed certificates used by Prometheus, Grafana and the collector.
2. Start the stack with `docker-compose up`.
3. Execute `python scripts/update_dashboards.py` to regenerate the dashboard JSON files in `grafana/dashboards/`.
4. Commit the JSON files to trigger the `Grafana Deploy` workflow which applies them to Grafana.

Running the update script ensures the dashboards stay current during local runs.

See [Grafana GitOps Workflow](grafana_gitops.md) for details on automated deployment.

