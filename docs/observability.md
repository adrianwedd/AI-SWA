# Observability Setup

AI-SWA services expose Prometheus metrics for local debugging. Two Grafana dashboards are provided:

- **improvement-dashboard.json** – tracks task throughput.
- **observer-dashboard.json** – monitors worker CPU, memory and aggregate task metrics.

## Usage

1. Run the stack with `docker-compose up` or start the services manually.
2. Execute `python scripts/update_dashboards.py` to regenerate the dashboard JSON files.
3. Import the JSON files into Grafana and set Prometheus as the data source.

Running the update script ensures the dashboards stay current during local runs.

