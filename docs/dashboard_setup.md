# Continuous Improvement Dashboard

The Grafana dashboard defined in `grafana/dashboard.py` visualizes key metrics exported by the services via Prometheus.

1. Install Prometheus and Grafana.
2. Run the AI-SWA services so that metrics are exposed (see `core/telemetry.py`).
3. Generate the dashboard JSON:
   ```bash
   python grafana/dashboard.py > improvement-dashboard.json
   ```
4. Import `improvement-dashboard.json` into Grafana and set the data source to your Prometheus instance.

The dashboard shows task execution counts, orchestrator run totals and average task duration to help track agent throughput over time.
