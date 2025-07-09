# Deploying AI-SWA with Terraform

This repository includes Terraform modules for installing the core services on a Kubernetes cluster via Helm. Modules live under `deploy/terraform/modules` and cover the following components:

- **orchestrator** – coordinates task execution
- **worker** – executes shell commands
- **broker** – REST API storing tasks and results
- **plugin marketplace** – serves plugins over HTTP and gRPC

## Setup

1. Install Terraform and ensure access to a Kubernetes cluster.
2. Configure the Helm provider by setting the `kubeconfig` variable if your config is not in `~/.kube/config`.
3. Choose a variables file for your environment:
   - `envs/staging.tfvars` – single replica deployment using `latest` images.
   - `envs/production.tfvars` – scaled deployment using `stable` tags.
4. Initialize the working directory:

```bash
cd deploy/terraform
terraform init
```

5. Review the plan and apply:

```bash
terraform plan -var-file=envs/staging.tfvars
terraform apply -var-file=envs/staging.tfvars
```

Swap in `envs/production.tfvars` for a production deployment. The modules will install the Helm charts defined under `deploy/helm/`.

