#!/bin/sh
set -euo pipefail
SCRIPT_DIR="$(dirname "$0")"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

# Generate TLS certificates
./observability/generate_certs.sh

# Start observability services
if command -v docker-compose >/dev/null 2>&1; then
    docker-compose up -d otel-collector prometheus grafana
else
    echo "docker-compose not found" >&2
    exit 1
fi

echo "Observability stack started"
