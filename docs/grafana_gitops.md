# Grafana GitOps Workflow

Dashboards for AI-SWA are managed as code and deployed automatically.

1. Run `python scripts/update_dashboards.py` to generate JSON files under
   `grafana/dashboards/`.
2. Commit the JSON files to version control. Any change to this directory triggers
   the `Grafana Deploy` workflow which applies the dashboards to the configured
   Grafana instance via its HTTP API.
3. Provide `GRAFANA_URL` and `GRAFANA_API_KEY` as repository secrets so the
   workflow can authenticate.

This approach keeps Grafana configuration fully declarative and reproducible.
