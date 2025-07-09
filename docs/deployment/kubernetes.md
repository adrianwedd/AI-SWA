# Deploying AI-SWA with Helm

This repository ships Helm charts for running the core services on a Kubernetes cluster. The charts live under `deploy/helm/` and cover the following components:

- **orchestrator** – coordinates task execution
- **worker** – executes shell commands from the broker
- **broker** – REST API storing tasks and results
- **plugin-marketplace** – serves plugins over HTTP and gRPC

## Basic Usage

1. Ensure the container images are available to your cluster (either build and push them or use the provided tags).
2. Choose a values file for your environment:
   - `values-dev.yaml` – single replica of each service using the `latest` tag.
   - `values-prod.yaml` – scaled-out deployment using the `stable` tag.
3. Install the charts:

```bash
helm install ai-swa deploy/helm -f deploy/helm/values-dev.yaml
```

Swap in `values-prod.yaml` for a production deployment. The command installs all charts in a single release using the settings from the chosen values file.

## Customization

Each subchart exposes common parameters such as `image.repository`, `image.tag` and `replicaCount`. Override them on the command line or create your own values file:

```bash
helm upgrade --install ai-swa deploy/helm \
  --set orchestrator.image.tag=v1.2.3 \
  --set broker.service.type=LoadBalancer
```

Refer to the `values.yaml` files in each chart for the full list of options.
