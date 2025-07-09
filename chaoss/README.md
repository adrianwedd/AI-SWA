# CHAOSS Community Metrics

This directory contains a minimal setup for tracking community health using the
[CHAOSS](https://chaoss.community/) metrics model.

## Running GrimoireLab
1. Install Docker and Docker Compose.
2. Start the metrics stack:
   ```bash
   docker compose -f docker-compose.yml up -d
   ```
   The stack exposes an Elasticsearch instance and prebuilt Grafana dashboards.

## Viewing the Dashboard
After the services start, visit `http://localhost:5601` for Kibana and
`http://localhost:3000` for Grafana. Dashboards visualize metrics like
*Time to First Response* and *Contributor Absence Factor* using data collected
from the repository.
