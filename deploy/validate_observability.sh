#!/bin/sh
set -euo pipefail
SCRIPT_DIR="$(dirname "$0")"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

# Check Prometheus health
curl -sk https://prometheus:9090/-/healthy > /dev/null

# Check Grafana health
curl -sk https://grafana:3000/api/health | grep -q 'database' > /dev/null

# Check collector metrics endpoint
curl -sk https://otel-collector:8888/metrics > /dev/null

# Validate that Prometheus scraped metrics for each service
for svc in broker worker orchestrator io-service; do
    if ! curl -skG https://prometheus:9090/api/v1/query --data-urlencode "query=up{service_name=\"$svc\"}" | grep -q '"value"'; then
        echo "Prometheus missing metrics for $svc" >&2
        exit 1
    fi
done

echo "Observability stack validated"
