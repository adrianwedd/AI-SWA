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
